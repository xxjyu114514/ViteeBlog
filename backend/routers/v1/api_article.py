import os
import uuid
import aiofiles
import traceback
import math
import hashlib
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, Body, HTTPException, status, UploadFile, File, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, func
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError

from dependencies import get_db, get_current_user, allow_admin_only, get_current_user_optional
from models.blog_models import Article, ArticleStatus, User, Category, Tag, UserRole, article_tag
from schemas.article_schema import ArticleCreate, ArticleReviewAction, ArticleDetailOut

router = APIRouter()

IMAGE_STORAGE = "storage/images"
ARTICLE_STORAGE = "storage/articles"
_upload_counter: dict = {}


# --- 接口 1：POST /upload-image (图片上传) ---
@router.post("/upload-image", summary="图片上传接口")
async def upload_article_image(file: UploadFile = File(...), user: User = Depends(get_current_user)):
    now = datetime.now()
    user_id = user.id
    if user_id not in _upload_counter:
        _upload_counter[user_id] = []
    _upload_counter[user_id] = [t for t in _upload_counter[user_id] if (now - t).total_seconds() < 3600]
    if len(_upload_counter[user_id]) >= 15:
        raise HTTPException(status_code=429, detail="上传过于频繁，请1小时后再试")

    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="只能上传图片文件")
    ext = os.path.splitext(file.filename)[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    os.makedirs(IMAGE_STORAGE, exist_ok=True)
    file_path = os.path.join(IMAGE_STORAGE, unique_name)
    try:
        content = await file.read()
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="文件大小不能超过10MB")
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)
        _upload_counter[user_id].append(now)
        return {"url": f"/storage/images/{unique_name}"}
    except Exception:
        raise HTTPException(status_code=500, detail="文件保存失败")


# --- 接口 2：DELETE /upload-image (图片删除) ---
@router.delete("/upload-image", summary="图片删除接口")
async def delete_article_image(filename: str, user: User = Depends(get_current_user)):
    file_path = os.path.join(IMAGE_STORAGE, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="图片不存在")
    try:
        os.remove(file_path)
        return {"message": "图片已删除"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除文件时出错: {str(e)}")


# --- 接口 3：POST /autosave (加入乐观锁逻辑) ---
@router.post("/autosave", summary="自动保存/草稿更新")
async def autosave(article_in: ArticleCreate, user: User = Depends(get_current_user),
                   db: AsyncSession = Depends(get_db)):
    tags = []
    if article_in.tag_ids:
        tag_res = await db.execute(select(Tag).where(Tag.id.in_(article_in.tag_ids)))
        tags = tag_res.scalars().all()

    if article_in.id:
        res = await db.execute(select(Article).where(Article.id == article_in.id).options(selectinload(Article.tags)))
        article = res.scalars().first()

        if not article or (article.user_id != user.id and user.role != UserRole.ADMIN):
            raise HTTPException(status_code=403, detail="无权修改此文章")

        if article_in.version is not None and article_in.version != article.version:
            raise HTTPException(status_code=409, detail="文章已被他人修改，请刷新后重新编辑")

        article.title = article_in.title
        article.summary = article_in.summary
        if article_in.cover_image is not None:
            article.cover_image = article_in.cover_image
        article.category_id = article_in.category_id
        article.updated_at = datetime.now()
        article.tags = tags

        if article_in.content is not None:
            new_hash = hashlib.md5(article_in.content.encode()).hexdigest()
            if article.content_hash != new_hash:
                article.content = article_in.content
                article.content_hash = new_hash
        article.version += 1
    else:
        if (not article_in.title or not article_in.title.strip()) and not article_in.content:
            raise HTTPException(status_code=400, detail="标题和内容不能同时为空")

        content_hash = hashlib.md5(article_in.content.encode()).hexdigest() if article_in.content else ""
        article = Article(
            title=article_in.title, summary=article_in.summary, content=article_in.content,
            content_hash=content_hash, category_id=article_in.category_id, user_id=user.id,
            cover_image=article_in.cover_image,
            status=ArticleStatus.DRAFT, tags=tags, version=1
        )
        db.add(article)

    await db.commit()
    await db.refresh(article)
    return {"id": article.id, "version": article.version, "message": "已自动保存"}


# --- 接口 4：PUT /{article_id}/publish (发布文章) ---
@router.put("/{article_id}/publish", summary="正式发布文章")
async def publish_article(article_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Article).where(Article.id == article_id))
    article = res.scalars().first()

    if not article or (article.user_id != user.id and user.role != UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="无权操作")

    if not article.title or not article.title.strip():
        raise HTTPException(status_code=400, detail="发布失败：标题不能为空")
    if not article.content or not article.content.strip():
        raise HTTPException(status_code=400, detail="发布失败：文章内容不能为空")

    if user.role == UserRole.ADMIN:
        article.status = ArticleStatus.PUBLISHED
        article.published_at = datetime.now()
    else:
        article.status = ArticleStatus.PENDING
        article.review_remark = None
        article.submitted_at = datetime.now()

    article.updated_at = datetime.now()
    await db.commit()
    return {"message": "发布成功" if user.role == UserRole.ADMIN else "已提交审核"}


# --- 接口 5：GET /{article_id} (获取详情) ---
@router.get("/{article_id}", response_model=ArticleDetailOut, summary="获取文章详情")
async def get_article_detail(article_id: int, user: Optional[User] = Depends(get_current_user_optional),
                             db: AsyncSession = Depends(get_db)):
    res = await db.execute(
        select(Article).where(Article.id == article_id).options(
            selectinload(Article.category), selectinload(Article.tags), selectinload(Article.author)
        )
    )
    article = res.scalars().first()
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")

    is_author = user and article.user_id == user.id
    is_admin = user and user.role == UserRole.ADMIN

    if article.deleted_at and not (is_author or is_admin):
        raise HTTPException(status_code=404, detail="文章已删除")

    if article.status != ArticleStatus.PUBLISHED:
        if not user:
            raise HTTPException(status_code=401, detail="请登录后查看私有文章")
        if not (is_author or is_admin):
            raise HTTPException(status_code=403, detail="无权访问该文章")

    # 使用原子操作增加阅读量，避免并发问题
    await db.execute(
        update(Article)
        .where(Article.id == article_id)
        .values(view_count=Article.view_count + 1)
    )
    await db.commit()

    return article


# --- 接口 6：POST /{article_id}/withdraw (撤回审核) ---
@router.post("/{article_id}/withdraw", summary="撤回发布")
async def withdraw_article(article_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Article).where(Article.id == article_id))
    article = res.scalars().first()
    if not article or (article.user_id != user.id and user.role != UserRole.ADMIN):
        raise HTTPException(status_code=403)

    if article.status != ArticleStatus.PENDING:
        raise HTTPException(status_code=400, detail="只有处于待审核状态的文章可以撤回")

    article.status = ArticleStatus.DRAFT
    await db.commit()
    return {"message": "已撤回至草稿状态"}


# --- 接口 7：POST /admin/articles/{article_id}/review (管理员审核) ---
@router.post("/admin/articles/{article_id}/review", summary="【管理员】审核文章")
async def review_article(article_id: int, action: ArticleReviewAction, admin: User = Depends(allow_admin_only),
                         db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Article).where(Article.id == article_id))
    article = res.scalars().first()
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")

    if article.status != ArticleStatus.PENDING:
        raise HTTPException(status_code=400, detail="该文章不处于待审核状态")

    if action.pass_audit:
        article.status = ArticleStatus.PUBLISHED
        article.review_remark = None
        article.reviewed_at = datetime.now()
        article.reviewed_by = admin.id
        article.published_at = datetime.now()
    else:
        if not action.remark or not action.remark.strip():
            raise HTTPException(status_code=400, detail="驳回文章必须填写驳回理由")
        article.status = ArticleStatus.DRAFT
        article.reviewed_at = datetime.now()
        article.reviewed_by = admin.id
        article.review_remark = action.remark

    await db.commit()
    return {"message": "审核操作成功"}


# --- 接口 8：GET /admin/pending (待审核列表) ---
@router.get("/admin/pending", summary="【管理员】待审核列表")
async def list_pending_articles(
        page: int = Query(1, ge=1),
        size: int = Query(20, ge=1),
        admin: User = Depends(allow_admin_only),
        db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Article)
        .where(Article.status == ArticleStatus.PENDING, Article.deleted_at == None)
        .order_by(Article.submitted_at.asc())
    )
    total_res = await db.execute(select(func.count()).select_from(stmt.subquery()))
    total = total_res.scalar() or 0
    res = await db.execute(stmt.offset((page - 1) * size).limit(size))
    return {
        "items": res.scalars().all(),
        "total": total,
        "page": page,
        "size": size,
        "pages": math.ceil(total / size) if total > 0 else 0
    }


# --- 接口 9：DELETE /{article_id} (软删除) ---
@router.delete("/{article_id}", summary="软删除")
async def soft_delete(article_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Article).where(Article.id == article_id))
    article = res.scalars().first()
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    if article.deleted_at:
        raise HTTPException(status_code=400, detail="文章已在回收站中")
    if user.role != UserRole.ADMIN and article.user_id != user.id:
        raise HTTPException(status_code=403, detail="无权删除此文章")

    article.deleted_at = datetime.now()
    await db.commit()
    return {"message": "已入回收站"}


# --- 接口 10：DELETE /{article_id}/hard (硬删除) ---
@router.delete("/{article_id}/hard", summary="硬删除")
async def hard_delete_article(article_id: int, user: User = Depends(get_current_user),
                              db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Article).where(Article.id == article_id))
    article = res.scalars().first()
    if not article or (article.user_id != user.id and user.role != UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="无权删除此文章")

    await db.delete(article)
    await db.commit()
    return {"message": "文章已永久删除"}


# --- 接口 11：POST /{article_id}/restore (恢复文章) ---
@router.post("/{article_id}/restore", summary="恢复文章")
async def restore_article(article_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = update(Article).where(Article.id == article_id)
    if user.role != UserRole.ADMIN: stmt = stmt.where(Article.user_id == user.id)
    await db.execute(stmt.values(deleted_at=None))
    await db.commit()
    return {"message": "已恢复"}


# --- 接口 12：GET /my/list (我的文章列表) ---
@router.get("/my/list", summary="我的文章列表")
async def get_my_articles(page: int = Query(1, ge=1), size: int = Query(10, ge=1),
                          status: Optional[ArticleStatus] = Query(None), user: User = Depends(get_current_user),
                          db: AsyncSession = Depends(get_db)):
    filters = [Article.user_id == user.id, Article.deleted_at == None]
    if status: filters.append(Article.status == status)
    query = select(Article).where(and_(*filters)).order_by(Article.created_at.desc())
    total_res = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_res.scalar() or 0
    res = await db.execute(query.offset((page - 1) * size).limit(size))
    return {"items": res.scalars().all(), "total": total, "page": page, "size": size, "pages": math.ceil(total / size)}


# --- 接口 13：GET /public/list (公开文章列表) ---
@router.get("/public/list", summary="公开文章列表")
async def list_public_articles(page: int = Query(1, ge=1), size: int = Query(10, ge=1),
                               category_id: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    filters = [Article.status == ArticleStatus.PUBLISHED, Article.deleted_at == None]
    if category_id: filters.append(Article.category_id == category_id)
    query = select(Article).where(and_(*filters)).order_by(Article.created_at.desc())
    total_res = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_res.scalar() or 0
    res = await db.execute(query.offset((page - 1) * size).limit(size))
    return {"items": res.scalars().all(), "total": total, "page": page, "size": size, "pages": math.ceil(total / size)}


# --- 接口 14：GET /admin/all-articles (全站文章列表) ---
@router.get("/admin/all-articles", summary="【管理员】全站文章列表")
async def list_all_articles_admin(page: int = Query(1, ge=1), size: int = Query(10, ge=1),
                                  show_deleted: bool = Query(False, description="是否显示已删除文章"),
                                  admin: User = Depends(allow_admin_only), db: AsyncSession = Depends(get_db)):
    filters = []
    if not show_deleted:
        filters.append(Article.deleted_at == None)

    query = select(Article).where(and_(*filters)).order_by(Article.created_at.desc())
    total_res = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_res.scalar() or 0
    res = await db.execute(query.offset((page - 1) * size).limit(size))
    return {"items": res.scalars().all(), "total": total, "page": page, "size": size, "pages": math.ceil(total / size)}