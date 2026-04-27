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
from schemas.article_schema import ArticleCreate, ArticleReviewAction

router = APIRouter()

IMAGE_STORAGE = "storage/images"
ARTICLE_STORAGE = "storage/articles"


# --- 1. 图片上传 (不允许修改) ---
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
            raise HTTPException(status_code=400, detail="文件大小不能超过10MB")
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)
        return {"url": f"/storage/images/{unique_name}"}
    except Exception:
        raise HTTPException(status_code=500, detail="文件保存失败")


# --- 2. 自动保存 (修改点：恢复权限逻辑、补全路径处理、确认标签) ---
@router.post("/autosave", summary="自动保存/草稿更新")
async def autosave(article_in: ArticleCreate, user: User = Depends(get_current_user),
                   db: AsyncSession = Depends(get_db)):
    # 标签处理逻辑
    tags = []
    if article_in.tag_ids:
        tag_res = await db.execute(select(Tag).where(Tag.id.in_(article_in.tag_ids)))
        found_tags = tag_res.scalars().all()
        # 验证所有传入的标签ID都存在
        if len(found_tags) != len(article_in.tag_ids):
            raise HTTPException(status_code=400, detail="部分标签ID不存在")
        tags = found_tags

    if article_in.id:
        # 更新分支
        res = await db.execute(select(Article).where(Article.id == article_in.id).options(selectinload(Article.tags)))
        article = res.scalars().first()

        # 恢复权限判断逻辑
        if not article or (article.user_id != user.id and user.role != UserRole.ADMIN):
            raise HTTPException(status_code=403, detail="无权修改此文章")

        # 只更新非 None 的字段，避免覆盖为空值
        if article_in.title is not None:
            article.title = article_in.title
        if article_in.summary is not None:
            article.summary = article_in.summary
        if article_in.category_id is not None:
            article.category_id = article_in.category_id
        article.updated_at = datetime.now()
        article.tags = tags

        if article_in.content is not None:
            new_hash = hashlib.md5(article_in.content.encode()).hexdigest()
            # 哈希比对逻辑
            if article.content_hash != new_hash:
                os.makedirs(ARTICLE_STORAGE, exist_ok=True)
                file_name = f"{uuid.uuid4().hex}.md"
                file_path = os.path.join(ARTICLE_STORAGE, file_name)
                async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
                    await f.write(article_in.content)
                article.content_path = file_path
                article.content_hash = new_hash
        # 补全 content_path 处理
        elif article_in.content_path:
            article.content_path = article_in.content_path
    else:
        # 新建分支
        if (not article_in.title or not article_in.title.strip()) and not article_in.content:
            raise HTTPException(status_code=400, detail="标题和内容不能同时为空")

        file_path = ""
        content_hash = ""
        if article_in.content:
            os.makedirs(ARTICLE_STORAGE, exist_ok=True)
            file_name = f"{uuid.uuid4().hex}.md"
            file_path = os.path.join(ARTICLE_STORAGE, file_name)
            async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
                await f.write(article_in.content)
            content_hash = hashlib.md5(article_in.content.encode()).hexdigest()

        article = Article(
            title=article_in.title,
            summary=article_in.summary,
            content_path=file_path or article_in.content_path,
            content_hash=content_hash,
            category_id=article_in.category_id,
            user_id=user.id,
            status=ArticleStatus.DRAFT,
            tags=tags
        )
        db.add(article)

    await db.commit()
    await db.refresh(article)
    return {"id": article.id, "message": "已自动保存"}


# --- 3. 正式发布 (修改点：Admin直发逻辑) ---
@router.put("/{article_id}/publish", summary="正式发布文章")
async def publish_article(article_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Article).where(Article.id == article_id))
    article = res.scalars().first()

    if not article or (article.user_id != user.id and user.role != UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="无权操作")

    if not article.title or not article.content_path:
        raise HTTPException(status_code=400, detail="标题或内容不能为空，无法发布")

    if not os.path.exists(article.content_path):
        raise HTTPException(status_code=500, detail="正文文件丢失")

    # 管理员免审直发
    if user.role == UserRole.ADMIN:
        article.status = ArticleStatus.PUBLISHED
        article.published_at = datetime.now()
    else:
        article.status = ArticleStatus.PENDING
        article.submitted_at = datetime.now()

    article.updated_at = datetime.now()
    await db.commit()
    return {"message": "发布成功" if user.role == UserRole.ADMIN else "已提交审核"}


# --- 4. 详情 (修改点：恢复完整权限逻辑) ---
@router.get("/{article_id}", summary="获取文章详情")
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

    # 权限校验
    is_author = user and article.user_id == user.id
    is_admin = user and user.role == UserRole.ADMIN

    # 软删除处理
    if article.deleted_at:
        if not (is_author or is_admin):
            raise HTTPException(status_code=404, detail="文章已删除")

    # 未发布文章处理
    if article.status != ArticleStatus.PUBLISHED:
        if not user:
            raise HTTPException(status_code=401, detail="请登录后查看私有文章")
        if not (is_author or is_admin):
            raise HTTPException(status_code=403, detail="无权访问该文章")

    return article


# --- 5. 撤回发布 (修改点：恢复状态校验) ---
@router.post("/{article_id}/withdraw", summary="撤回发布")
async def withdraw_article(article_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Article).where(Article.id == article_id))
    article = res.scalars().first()
    if not article or (article.user_id != user.id and user.role != UserRole.ADMIN):
        raise HTTPException(status_code=403)

    # 状态校验：只有待审核可以撤回
    if article.status != ArticleStatus.PENDING:
        raise HTTPException(status_code=400, detail="只有处于待审核状态的文章可以撤回")

    article.status = ArticleStatus.DRAFT
    await db.commit()
    return {"message": "已撤回至草稿状态"}


# --- 6. 管理员审核 (修改点：恢复完整审核逻辑) ---
@router.post("/admin/articles/{article_id}/review", summary="【管理员】审核文章")
async def review_article(article_id: int, action: ArticleReviewAction, admin: User = Depends(allow_admin_only),
                         db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Article).where(Article.id == article_id))
    article = res.scalars().first()
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")

    # 校验状态
    if article.status != ArticleStatus.PENDING:
        raise HTTPException(status_code=400, detail="该文章不处于待审核状态")

    if action.pass_audit:
        article.status = ArticleStatus.PUBLISHED
        article.reviewed_at = datetime.now()
        article.reviewed_by = admin.id
        article.published_at = datetime.now()
    else:
        # 驳回校验
        if not action.remark or not action.remark.strip():
            raise HTTPException(status_code=400, detail="驳回文章必须填写驳回理由")
        article.status = ArticleStatus.DRAFT
        article.reviewed_at = datetime.now()
        article.reviewed_by = admin.id
        article.review_remark = action.remark

    await db.commit()
    return {"message": "审核操作成功"}


# --- 7. 待审核列表 (不允许修改) ---
@router.get("/admin/pending", summary="【管理员】待审核列表")
async def list_pending_articles(admin: User = Depends(allow_admin_only), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Article).where(Article.status == ArticleStatus.PENDING))
    return res.scalars().all()


# --- 8. 软删除 (不允许修改) ---
@router.delete("/{article_id}", summary="软删除")
async def soft_delete(article_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Article).where(Article.id == article_id))
    article = res.scalars().first()
    
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    # 检查是否已被删除
    if article.deleted_at:
        raise HTTPException(status_code=400, detail="文章已在回收站中")
    
    # 权限校验
    if user.role != UserRole.ADMIN and article.user_id != user.id:
        raise HTTPException(status_code=403, detail="无权删除此文章")
    
    article.deleted_at = datetime.now()
    await db.commit()
    return {"message": "已入回收站"}


# --- 9. 硬删除 (不允许修改) ---
@router.delete("/{article_id}/hard", summary="硬删除")
async def hard_delete_article(article_id: int, user: User = Depends(get_current_user),
                              db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Article).where(Article.id == article_id))
    article = res.scalars().first()
    if not article or (article.user_id != user.id and user.role != UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="无权删除此文章")
    
    # 删除关联的 Markdown 文件
    if article.content_path and os.path.exists(article.content_path):
        try:
            os.remove(article.content_path)
        except Exception as e:
            print(f"警告：删除文件失败 {article.content_path}: {str(e)}")
    
    await db.delete(article)
    await db.commit()
    return {"message": "文章已永久删除"}


# --- 10. 恢复 (不允许修改) ---
@router.post("/{article_id}/restore", summary="恢复文章")
async def restore_article(article_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = update(Article).where(Article.id == article_id)
    if user.role != UserRole.ADMIN: stmt = stmt.where(Article.user_id == user.id)
    await db.execute(stmt.values(deleted_at=None))
    await db.commit()
    return {"message": "已恢复"}


# --- 11. 用户角色修改 (修改点：恢复安全校验) ---
@router.put("/admin/users/{user_id}/role", summary="【超级管理员】修改用户角色")
async def update_user_role(user_id: int, new_role: UserRole = Body(..., embed=True),
                           admin: User = Depends(allow_admin_only), db: AsyncSession = Depends(get_db)):
    # 安全校验：不能修改自己
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="不能修改自己的角色")

    res = await db.execute(select(User).where(User.id == user_id))
    target_user = res.scalars().first()
    # 校验目标是否存在
    if not target_user:
        raise HTTPException(status_code=404, detail="目标用户不存在")

    # 降级管理员校验
    if target_user.role == UserRole.ADMIN and new_role != UserRole.ADMIN:
        admin_count_res = await db.execute(select(func.count(User.id)).where(User.role == UserRole.ADMIN))
        if admin_count_res.scalar() <= 1:
            raise HTTPException(status_code=400, detail="全站必须至少保留一名管理员")

    target_user.role = new_role
    await db.commit()
    return {"message": f"成功将用户角色更新为 {new_role}"}


# --- 12. 我的列表 (不允许修改) ---
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
    return {"items": res.scalars().all(), "total": total, "page": page, "pages": math.ceil(total / size)}


# --- 13. 公开列表 (不允许修改) ---
@router.get("/public/list", summary="公开文章列表")
async def list_public_articles(page: int = Query(1, ge=1), size: int = Query(10, ge=1),
                               category_id: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    filters = [Article.status == ArticleStatus.PUBLISHED, Article.deleted_at == None]
    if category_id: filters.append(Article.category_id == category_id)
    query = select(Article).where(and_(*filters)).order_by(Article.created_at.desc())
    total_res = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_res.scalar() or 0
    res = await db.execute(query.offset((page - 1) * size).limit(size))
    return {"items": res.scalars().all(), "total": total, "page": page, "pages": math.ceil(total / size)}


# --- 14. 全站列表 (不允许修改) ---
@router.get("/admin/all-articles", summary="【管理员】全站文章列表")
async def list_all_articles_admin(page: int = Query(1, ge=1), size: int = Query(10, ge=1),
                                  show_deleted: bool = Query(False, description="是否显示已删除文章"),
                                  admin: User = Depends(allow_admin_only), db: AsyncSession = Depends(get_db)):
    filters = []
    if not show_deleted:
        filters.append(Article.deleted_at == None)
    
    query = select(Article).where(and_(*filters)).order_by(Article.created_at.desc()) if filters else select(Article).order_by(Article.created_at.desc())
    total_res = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_res.scalar() or 0
    res = await db.execute(query.offset((page - 1) * size).limit(size))
    return {"items": res.scalars().all(), "total": total, "page": page, "pages": math.ceil(total / size)}