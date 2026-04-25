import os
import uuid
import aiofiles
import traceback
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, Body, HTTPException, status, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, func
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError

from dependencies import get_db, get_current_user, allow_admin_only
from models.blog_models import Article, ArticleStatus, User, Category, Tag, UserRole
from schemas.article_schema import ArticleCreate, ArticleReviewAction

router = APIRouter()

IMAGE_STORAGE = "storage/images"


# --- 1. 图片上传 (保留原逻辑) ---
@router.post("/upload-image", summary="图片上传接口")
async def upload_article_image(file: UploadFile = File(...), user: User = Depends(get_current_user)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="只能上传图片文件")
    ext = os.path.splitext(file.filename)[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    os.makedirs(IMAGE_STORAGE, exist_ok=True)
    file_path = os.path.join(IMAGE_STORAGE, unique_name)
    try:
        content = await file.read()
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="图片大小不能超过10MB")
        async with aiofiles.open(file_path, mode="wb") as f:
            await f.write(content)
        return {"url": f"/static/{file_path}".replace("\\", "/")}
    except Exception:
        raise HTTPException(status_code=500, detail="图片保存失败")


# --- 2. 自动保存/修改文章 (包含状态锁定逻辑) ---
@router.post("/autosave", summary="保存文章/草稿")
async def autosave_article(
        article_in: ArticleCreate,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    try:
        # 处理标签对象
        db_tags = []
        if article_in.tag_ids:
            tag_res = await db.execute(select(Tag).where(Tag.id.in_(article_in.tag_ids)))
            db_tags = tag_res.scalars().all()

        if article_in.id:
            res = await db.execute(
                select(Article).where(Article.id == article_in.id).options(selectinload(Article.tags)))
            db_article = res.scalars().first()
            if not db_article: raise HTTPException(status_code=404, detail="文章不存在")

            # 权限检查
            if db_article.user_id != user.id and user.role != UserRole.ADMIN:
                raise HTTPException(status_code=403, detail="无权修改")

            # 核心逻辑：待审核状态下禁止编辑内容
            if db_article.status == ArticleStatus.PENDING:
                raise HTTPException(status_code=400, detail="文章正在审核中，无法修改内容。请先撤回。")

            # 更新数据
            db_article.title = article_in.title
            db_article.summary = article_in.summary
            db_article.content_path = article_in.content_path
            db_article.category_id = article_in.category_id
            db_article.tags = db_tags
            # 注意：保存草稿不改变 status，除非显式传值，但通常交给 publish 接口处理状态流转
        else:
            # 新建文章
            db_article = Article(
                title=article_in.title,
                summary=article_in.summary,
                content_path=article_in.content_path,
                category_id=article_in.category_id,
                user_id=user.id,
                tags=db_tags,
                status=ArticleStatus.DRAFT
            )
            db.add(db_article)

        await db.commit()
        return {"message": "已保存", "article_id": db_article.id}
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="分类ID不存在或数据异常")


# --- 3. 提交审核/正式发布 ---
@router.put("/{article_id}/publish", summary="提交审核或免审发布")
async def publish_article(article_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Article).where(Article.id == article_id))
    article = res.scalars().first()
    if not article or article.user_id != user.id:
        raise HTTPException(status_code=403, detail="文章不存在或无权操作")

    # 管理员免审直发
    if user.role == UserRole.ADMIN:
        article.status = ArticleStatus.PUBLISHED
        article.published_at = datetime.now()
        await db.commit()
        return {"message": "管理员文章，已直接发布"}

    # 普通用户防灌水检查 (待审核数量限制)
    pending_count = await db.execute(
        select(func.count(Article.id)).where(Article.user_id == user.id, Article.status == ArticleStatus.PENDING)
    )
    if pending_count.scalar() >= 3:
        raise HTTPException(status_code=400, detail="您已有3篇待审核文章，请等待管理员处理后再提交")

    # 状态流转：Draft/Rejected -> Pending
    article.status = ArticleStatus.PENDING
    article.submitted_at = datetime.now()
    article.review_remark = None  # 清空之前的驳回理由
    await db.commit()
    return {"message": "已提交，等待管理员审核"}


# --- 4. 撤回文章 ---
@router.post("/{article_id}/withdraw", summary="撤回审核中的文章")
async def withdraw_article(article_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Article).where(Article.id == article_id))
    article = res.scalars().first()
    if not article or article.user_id != user.id:
        raise HTTPException(status_code=403)

    if article.status != ArticleStatus.PENDING:
        raise HTTPException(status_code=400, detail="只有待审核状态的文章可以撤回")

    article.status = ArticleStatus.DRAFT
    await db.commit()
    return {"message": "已撤回为草稿"}


# --- 5. 管理员审核接口 (通过/驳回) ---
@router.post("/admin/articles/{article_id}/review", summary="管理员审核动作")
async def review_article(
        article_id: int,
        action: ArticleReviewAction,
        admin: User = Depends(allow_admin_only),
        db: AsyncSession = Depends(get_db)
):
    res = await db.execute(select(Article).where(Article.id == article_id))
    article = res.scalars().first()
    if not article or article.status != ArticleStatus.PENDING:
        raise HTTPException(status_code=400, detail="文章不存在或不在待审状态")

    article.reviewed_at = datetime.now()
    article.reviewed_by = admin.id

    if action.pass_audit:
        article.status = ArticleStatus.PUBLISHED
        msg = "审核通过，文章已发布"
    else:
        if not action.remark:
            raise HTTPException(status_code=400, detail="驳回请填写理由")
        article.status = ArticleStatus.DRAFT
        article.review_remark = action.remark
        msg = f"文章已驳回：{action.remark}"

    await db.commit()
    return {"message": msg}


# --- 6. 管理员：待审核列表 ---
@router.get("/admin/pending", summary="获取待审核文章列表")
async def list_pending_articles(admin: User = Depends(allow_admin_only), db: AsyncSession = Depends(get_db)):
    res = await db.execute(
        select(Article)
        .where(Article.status == ArticleStatus.PENDING, Article.deleted_at == None)
        .order_by(Article.submitted_at.asc())  # 按提交时间排序，先提交先处理
        .options(selectinload(Article.category), selectinload(Article.author))
    )
    return res.scalars().all()


# --- 7. 我的文章 (区分状态) ---
@router.get("/my-articles", summary="获取当前用户的文章列表")
async def get_my_articles(
        status: Optional[ArticleStatus] = None,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    query = select(Article).where(Article.user_id == user.id, Article.deleted_at == None)
    if status:
        query = query.where(Article.status == status)
    res = await db.execute(query.order_by(Article.updated_at.desc()).options(selectinload(Article.category)))
    return res.scalars().all()


# --- 8. 全站列表 (仅已发布) ---
@router.get("/list", summary="公开文章列表")
async def list_public_articles(page: int = Query(1), size: int = Query(10), db: AsyncSession = Depends(get_db)):
    res = await db.execute(
        select(Article)
        .where(Article.status == ArticleStatus.PUBLISHED, Article.deleted_at == None)
        .order_by(Article.created_at.desc())
        .offset((page - 1) * size).limit(size)
        .options(selectinload(Article.category))
    )
    return res.scalars().all()


# --- 9. 获取文章详情 ---
@router.get("/{article_id}", summary="获取文章详情")
async def get_article_detail(article_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(
        select(Article)
        .where(Article.id == article_id, Article.deleted_at == None)
        .options(
            selectinload(Article.category),
            selectinload(Article.tags),
            selectinload(Article.author)
        )
    )
    article = res.scalars().first()
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在或已被删除")
    return article


# --- 10. 软删除/硬删除/恢复 (保留原逻辑) ---
@router.delete("/{article_id}", summary="软删除")
async def soft_delete(article_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = update(Article).where(Article.id == article_id)
    if user.role != UserRole.ADMIN: stmt = stmt.where(Article.user_id == user.id)
    res = await db.execute(stmt.values(deleted_at=datetime.now()))
    if res.rowcount == 0: raise HTTPException(status_code=404)
    await db.commit()
    return {"message": "已入回收站"}


@router.delete("/{article_id}/hard", summary="硬删除")
async def hard_delete(article_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Article).where(Article.id == article_id))
    article = res.scalars().first()
    if not article or (article.user_id != user.id and user.role != UserRole.ADMIN):
        raise HTTPException(status_code=403)
    await db.delete(article)
    await db.commit()
    return {"message": "永久删除"}


@router.post("/{article_id}/restore", summary="恢复文章")
async def restore(article_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = update(Article).where(Article.id == article_id, Article.user_id == user.id)
    await db.execute(stmt.values(deleted_at=None))
    await db.commit()
    return {"message": "已恢复"}