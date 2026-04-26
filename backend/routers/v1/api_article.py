import os
import uuid
import aiofiles
import traceback
import math
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, Body, HTTPException, status, UploadFile, File, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, func
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError

# 确保导入项目依赖
from dependencies import get_db, get_current_user, allow_admin_only, get_current_user_optional
from models.blog_models import Article, ArticleStatus, User, Category, Tag, UserRole, article_tag
from schemas.article_schema import ArticleCreate, ArticleReviewAction

router = APIRouter()

IMAGE_STORAGE = "storage/images"
ARTICLE_STORAGE = "storage/articles"


# --- 1. 图片上传 ---
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
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)
        return {"url": f"/static/{file_path}"}
    except Exception:
        raise HTTPException(status_code=500, detail="图片保存失败")


# --- 2. 自动保存（修复逻辑 5） ---
@router.post("/autosave", summary="自动保存文章")
async def autosave(article_in: ArticleCreate, user: User = Depends(get_current_user),
                   db: AsyncSession = Depends(get_db)):
    # 基础校验：分类
    cat_res = await db.execute(select(Category).where(Category.id == article_in.category_id))
    if not cat_res.scalars().first():
        raise HTTPException(status_code=400, detail="分类不存在")

    # 处理标签
    tags = []
    if article_in.tag_ids:
        tag_res = await db.execute(select(Tag).where(Tag.id.in_(article_in.tag_ids)))
        tags = tag_res.scalars().all()

    if article_in.id:
        # 更新分支
        res = await db.execute(
            select(Article).where(Article.id == article_in.id).options(selectinload(Article.tags))
        )
        db_article = res.scalars().first()
        if not db_article or (db_article.user_id != user.id and user.role != UserRole.ADMIN):
            raise HTTPException(status_code=403, detail="无权操作此文章")

        db_article.title = article_in.title
        db_article.summary = article_in.summary
        db_article.category_id = article_in.category_id
        db_article.tags = tags

        # 补上 content_path 处理逻辑 (修复点 5)
        if article_in.content:
            file_name = f"{uuid.uuid4().hex}.md"
            os.makedirs(ARTICLE_STORAGE, exist_ok=True)
            file_path = os.path.join(ARTICLE_STORAGE, file_name)
            async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
                await f.write(article_in.content)
            db_article.content_path = file_path
        elif article_in.content_path:
            db_article.content_path = article_in.content_path
    else:
        # 新建分支
        path = article_in.content_path
        if article_in.content:
            file_name = f"{uuid.uuid4().hex}.md"
            os.makedirs(ARTICLE_STORAGE, exist_ok=True)
            path = os.path.join(ARTICLE_STORAGE, file_name)
            async with aiofiles.open(path, "w", encoding="utf-8") as f:
                await f.write(article_in.content)

        db_article = Article(
            title=article_in.title,
            summary=article_in.summary,
            content_path=path,
            category_id=article_in.category_id,
            user_id=user.id,
            status=ArticleStatus.DRAFT,
            tags=tags
        )
        db.add(db_article)

    await db.commit()
    await db.refresh(db_article)
    return db_article


# --- 3. 发布文章（修复逻辑 1） ---
@router.put("/{article_id}/publish", summary="正式发布文章")
async def publish_article(article_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Article).where(Article.id == article_id))
    article = res.scalars().first()
    if not article or article.user_id != user.id:
        raise HTTPException(status_code=403, detail="文章不存在或无权操作")

    # 1. 标题校验
    if not article.title or not article.title.strip():
        raise HTTPException(status_code=400, detail="发布失败：标题不能为空")

    # 2. 文件存在性校验
    if not article.content_path or not os.path.exists(article.content_path):
        raise HTTPException(status_code=400, detail="发布失败：文章内容文件不存在")

    # 3. 文件内容校验
    try:
        async with aiofiles.open(article.content_path, "r", encoding="utf-8") as f:
            content = await f.read()
            if not content.strip():
                raise HTTPException(status_code=400, detail="发布失败：文章内容不能为空")
    except Exception:
        raise HTTPException(status_code=500, detail="读取文章内容失败")

    # 逻辑流转
    if user.role == UserRole.ADMIN:
        article.status = ArticleStatus.PUBLISHED
    else:
        article.status = ArticleStatus.PENDING

    await db.commit()
    return {"message": "发布成功" if user.role == UserRole.ADMIN else "已提交审核"}


# --- 4. 获取详情（修复逻辑 3） ---
@router.get("/{article_id}", summary="获取文章详情")
async def get_article_detail(article_id: int, user: Optional[User] = Depends(get_current_user_optional),
                             db: AsyncSession = Depends(get_db)):
    stmt = select(Article).where(Article.id == article_id).options(
        selectinload(Article.category),
        selectinload(Article.tags)
    )
    res = await db.execute(stmt)
    article = res.scalars().first()

    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")

    # 权限判断
    is_owner_or_admin = user and (article.user_id == user.id or user.role == UserRole.ADMIN)

    # 状态判断逻辑
    is_deleted = article.deleted_at is not None
    is_not_published = article.status != ArticleStatus.PUBLISHED

    if is_deleted or is_not_published:
        if not user:
            # 未登录用户访问非公开文章
            raise HTTPException(status_code=401, detail="请登录后查看")
        if not is_owner_or_admin:
            # 已登录但不是作者或管理员
            raise HTTPException(status_code=403, detail="无权查看该文章")

    return article


# --- 5. 撤回审核（修复逻辑 7） ---
@router.post("/{article_id}/withdraw", summary="撤回发布申请")
async def withdraw_article(article_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Article).where(Article.id == article_id, Article.user_id == user.id))
    article = res.scalars().first()
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")

    # 状态校验 (修复点 7)
    if article.status != ArticleStatus.PENDING:
        raise HTTPException(status_code=400, detail="只有处于待审核状态的文章可以撤回")

    article.status = ArticleStatus.DRAFT
    await db.commit()
    return {"message": "已撤回为草稿状态"}


# --- 6. 管理员审核（修复逻辑 2） ---
@router.post("/admin/articles/{article_id}/review", summary="【管理员】审核文章")
async def review_article(article_id: int, action: ArticleReviewAction, admin: User = Depends(allow_admin_only),
                         db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Article).where(Article.id == article_id))
    article = res.scalars().first()
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")

    # 1. 校验必须是 PENDING 状态
    if article.status != ArticleStatus.PENDING:
        raise HTTPException(status_code=400, detail="该文章不在待审核队列中")

    # 2. 驳回必须填写备注
    if not action.pass_audit:
        if not action.remark or not action.remark.strip():
            raise HTTPException(status_code=400, detail="驳回文章必须填写原因")
        article.status = ArticleStatus.DRAFT
        # 假设模型中有审核备注字段
        if hasattr(article, 'review_remark'):
            article.review_remark = action.remark
    else:
        article.status = ArticleStatus.PUBLISHED

    # 3. 记录审核信息 (假设模型中包含这些审计字段)
    if hasattr(article, 'reviewed_at'):
        article.reviewed_at = datetime.now()
    if hasattr(article, 'reviewed_by'):
        article.reviewed_by = admin.id

    await db.commit()
    return {"message": "审核操作成功"}


# --- 7. 管理员待审列表 ---
@router.get("/admin/pending", summary="【管理员】待审核列表")
async def list_pending_articles(admin: User = Depends(allow_admin_only), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Article).where(Article.status == ArticleStatus.PENDING))
    return res.scalars().all()


# --- 8. 软删除/硬删除/恢复 ---
@router.delete("/{article_id}", summary="软删除文章")
async def soft_delete_article(article_id: int, user: User = Depends(get_current_user),
                              db: AsyncSession = Depends(get_db)):
    stmt = update(Article).where(Article.id == article_id)
    if user.role != UserRole.ADMIN:
        stmt = stmt.where(Article.user_id == user.id)
    result = await db.execute(stmt.values(deleted_at=datetime.now()))
    if result.rowcount == 0:
        raise HTTPException(status_code=403, detail="操作失败")
    await db.commit()
    return {"message": "已移至回收站"}


@router.delete("/{article_id}/hard", summary="硬删除文章")
async def hard_delete_article(article_id: int, user: User = Depends(get_current_user),
                              db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Article).where(Article.id == article_id))
    article = res.scalars().first()
    if not article or (article.user_id != user.id and user.role != UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="无权操作")
    await db.delete(article)
    await db.commit()
    return {"message": "已彻底删除"}


@router.post("/{article_id}/restore", summary="恢复文章")
async def restore_article(article_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = update(Article).where(Article.id == article_id)
    if user.role != UserRole.ADMIN:
        stmt = stmt.where(Article.user_id == user.id)
    await db.execute(stmt.values(deleted_at=None))
    await db.commit()
    return {"message": "文章已恢复"}


# --- 9. 管理员权限调整 ---
@router.put("/admin/users/{target_user_id}/role", summary="【管理员】调整用户权限")
async def update_user_role(target_user_id: int, new_role: UserRole = Body(..., embed=True),
                           admin: User = Depends(allow_admin_only), db: AsyncSession = Depends(get_db)):
    if admin.id == target_user_id:
        raise HTTPException(status_code=400, detail="禁止修改自己的权限")
    res = await db.execute(select(User).where(User.id == target_user_id))
    target_user = res.scalars().first()
    if not target_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if target_user.role == UserRole.ADMIN and new_role != UserRole.ADMIN:
        count_res = await db.execute(select(func.count()).select_from(User).where(User.role == UserRole.ADMIN))
        if count_res.scalar() <= 1:
            raise HTTPException(status_code=400, detail="必须保留至少一名管理员")
    target_user.role = new_role
    await db.commit()
    return {"message": "角色更新成功"}


# --- 10. 列表获取（修复逻辑 4 & 6） ---

@router.get("/my/list", summary="我的文章列表")
async def get_my_articles(
        page: int = Query(1, ge=1),
        size: int = Query(10, ge=1),
        status: Optional[ArticleStatus] = Query(None),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    filters = [Article.user_id == user.id, Article.deleted_at == None]
    if status:
        filters.append(Article.status == status)

    # 增加创建时间倒序 (修复点 4)
    query = select(Article).where(and_(*filters)).order_by(Article.created_at.desc())

    total_res = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_res.scalar() or 0

    res = await db.execute(query.offset((page - 1) * size).limit(size))
    return {
        "items": res.scalars().all(),
        "total": total,
        "page": page,
        "pages": math.ceil(total / size)
    }


@router.get("/public/list", summary="公开文章列表")
async def list_public_articles(
        page: int = Query(1, ge=1),
        size: int = Query(10, ge=1),
        category_id: Optional[int] = None,
        db: AsyncSession = Depends(get_db)
):
    filters = [Article.status == ArticleStatus.PUBLISHED, Article.deleted_at == None]
    if category_id:
        filters.append(Article.category_id == category_id)

    query = select(Article).where(and_(*filters)).order_by(Article.created_at.desc())

    # 修改返回格式为统一的分页格式 (修复点 6)
    total_res = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_res.scalar() or 0

    res = await db.execute(query.offset((page - 1) * size).limit(size))
    return {
        "items": res.scalars().all(),
        "total": total,
        "page": page,
        "pages": math.ceil(total / size)
    }