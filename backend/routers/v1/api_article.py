import os
import time
import uuid
import aiofiles
import traceback
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, Body, HTTPException, status, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.orm import selectinload
from dependencies import get_db, get_current_user, allow_admin_only
from models.blog_models import Article, ArticleStatus, User, Category, Tag, UserRole

router = APIRouter()

ARTICLE_STORAGE = "storage/articles"
IMAGE_STORAGE = "storage/images"


# --- 图片上传 ---
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
            raise HTTPException(status_code=400, detail="图片太大了")
        async with aiofiles.open(file_path, mode='wb') as f:
            await f.write(content)
        return {"url": f"/static/storage/images/{unique_name}", "filename": file.filename}
    except Exception:
        raise HTTPException(status_code=500, detail="图片保存失败")


# --- 用户权限管理 ---
@router.put("/admin/users/{target_user_id}/role", summary="【管理员专用】调整用户权限")
async def update_user_role(
        target_user_id: int,
        new_role: UserRole = Body(..., embed=True),
        current_admin: User = Depends(allow_admin_only),
        db: AsyncSession = Depends(get_db)
):
    if target_user_id == current_admin.id:
        raise HTTPException(status_code=400, detail="不能修改自己的权限")
    res = await db.execute(select(User).where(User.id == target_user_id))
    target_user = res.scalars().first()
    if not target_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if target_user.role == UserRole.ADMIN and new_role == UserRole.COMMON:
        admin_count_res = await db.execute(select(func.count(User.id)).where(User.role == UserRole.ADMIN))
        if admin_count_res.scalar() <= 1:
            raise HTTPException(status_code=400, detail="系统必须保留至少一名管理员")
    target_user.role = new_role
    await db.commit()
    return {"message": "权限更新成功"}


# --- 文章核心逻辑 (已健全分类与标签关联) ---
@router.post("/autosave", summary="自动保存（集成分类标签）")
async def autosave_article(
        title: str = Body(...),
        content: str = Body(...),
        article_id: Optional[int] = Body(None),
        category_id: Optional[int] = Body(None),
        tag_ids: List[int] = Body([], description="标签ID列表"),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    try:
        # 1. 验证分类是否存在
        if category_id:
            cat_res = await db.execute(select(Category).where(Category.id == category_id))
            if not cat_res.scalars().first():
                raise HTTPException(status_code=400, detail="所选分类不存在")

        # 2. 准备标签列表
        tags_list = []
        if tag_ids:
            tag_res = await db.execute(select(Tag).where(Tag.id.in_(tag_ids)))
            tags_list = list(tag_res.scalars().all())

        article = None
        if article_id:
            # 加载 tags 关系以便更新
            res = await db.execute(
                select(Article).options(selectinload(Article.tags)).where(Article.id == article_id)
            )
            article = res.scalars().first()
            if not article or (article.user_id != user.id and user.role != UserRole.ADMIN):
                raise HTTPException(status_code=403, detail="无权操作")
            file_path = article.content_path
        else:
            os.makedirs(ARTICLE_STORAGE, exist_ok=True)
            file_path = os.path.join(ARTICLE_STORAGE, f"user{user.id}_{int(time.time())}.md")

        async with aiofiles.open(file_path, mode='w', encoding='utf-8') as f:
            await f.write(content)

        if not article_id:
            # 新建并绑定
            article = Article(
                title=title,
                summary=content[:200].replace("#", "").strip(),
                content_path=file_path,
                user_id=user.id,
                category_id=category_id,
                is_audited=False,
                tags=tags_list
            )
            db.add(article)
        else:
            # 更新并重新绑定
            article.title = title
            article.category_id = category_id
            article.is_audited = False
            article.summary = content[:200].replace("#", "").strip()
            article.tags = tags_list

        await db.commit()
        return {"article_id": article.id, "message": "已同步"}
    except HTTPException as he:
        raise he
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=500, detail="保存失败")


# --- 列表逻辑 ---

@router.get("/list/public", summary="首页公共列表 (分页+关系)")
async def get_public_articles(
        category_id: Optional[int] = None,
        page: int = Query(1, ge=1, description="页码"),
        size: int = Query(10, ge=1, le=100, description="每页数量"),
        db: AsyncSession = Depends(get_db)
):
    # 构建基础查询条件
    filters = [Article.status == ArticleStatus.PUBLISHED, Article.deleted_at.is_(None)]
    if category_id:
        filters.append(Article.category_id == category_id)

    # 查询总数
    count_stmt = select(func.count(Article.id)).where(and_(*filters))
    total = (await db.execute(count_stmt)).scalar()

    # 分页查询数据 (加载分类和标签关系)
    stmt = select(Article).options(selectinload(Article.category), selectinload(Article.tags)) \
        .where(and_(*filters)).order_by(Article.published_at.desc())
    stmt = stmt.limit(size).offset((page - 1) * size)

    result = await db.execute(stmt)
    articles = result.scalars().all()

    return {
        "items": articles,
        "total": total,
        "page": page,
        "size": size
    }


@router.get("/user/my-articles", summary="获取我的文章列表")
async def get_my_articles(
        page: int = Query(1, ge=1),
        size: int = Query(10, ge=1, le=50),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    filters = [Article.user_id == user.id, Article.deleted_at.is_(None)]
    total = (await db.execute(select(func.count(Article.id)).where(and_(*filters)))).scalar()

    stmt = select(Article).where(and_(*filters)).order_by(Article.created_at.desc())
    stmt = stmt.limit(size).offset((page - 1) * size)

    res = await db.execute(stmt)
    return {"items": res.scalars().all(), "total": total}


@router.get("/admin/all-articles", summary="【管理员专用】获取全站所有文章")
async def admin_get_all_articles(
        page: int = Query(1, ge=1),
        size: int = Query(20, ge=1),
        user: User = Depends(allow_admin_only),
        db: AsyncSession = Depends(get_db)
):
    total = (await db.execute(select(func.count(Article.id)))).scalar()
    res = await db.execute(
        select(Article).options(selectinload(Article.author))
        .order_by(Article.created_at.desc())
        .limit(size).offset((page - 1) * size)
    )
    return {"items": res.scalars().all(), "total": total}


# --- 详情获取 (含分类标签) ---

@router.get("/{article_id}", summary="获取详情 (含元数据)")
async def get_article_detail(article_id: int, db: AsyncSession = Depends(get_db)):
    # 预加载作者、分类、标签
    res = await db.execute(
        select(Article)
        .options(selectinload(Article.author), selectinload(Article.category), selectinload(Article.tags))
        .where(Article.id == article_id, Article.deleted_at.is_(None))
    )
    article = res.scalars().first()
    if not article: raise HTTPException(status_code=404, detail="文章不存在")

    content = ""
    if os.path.exists(article.content_path):
        async with aiofiles.open(article.content_path, mode='r', encoding='utf-8') as f:
            content = await f.read()

    article.view_count += 1
    await db.commit()

    return {
        "info": article,
        "content": content,
        "category_name": article.category.name if article.category else "未分类",
        "tags": [t.name for t in article.tags]
    }


@router.delete("/{article_id}", summary="移至回收站")
async def soft_delete_article(article_id: int, user: User = Depends(get_current_user),
                              db: AsyncSession = Depends(get_db)):
    stmt = update(Article).where(Article.id == article_id)
    if user.role != UserRole.ADMIN: stmt = stmt.where(Article.user_id == user.id)
    result = await db.execute(stmt.values(deleted_at=datetime.now()))
    if result.rowcount == 0: raise HTTPException(status_code=403)
    await db.commit()
    return {"message": "已删除"}


@router.post("/{article_id}/restore", summary="恢复文章")
async def restore_article(article_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = update(Article).where(Article.id == article_id)
    if user.role != UserRole.ADMIN: stmt = stmt.where(Article.user_id == user.id)
    await db.execute(stmt.values(deleted_at=None))
    await db.commit()
    return {"message": "已恢复"}


@router.put("/admin/articles/{article_id}/audit", summary="【管理员专用】审核通过")
async def audit_article(article_id: int, admin: User = Depends(allow_admin_only), db: AsyncSession = Depends(get_db)):
    await db.execute(update(Article).where(Article.id == article_id).values(is_audited=True))
    await db.commit()
    return {"message": "已审核"}


@router.put("/{article_id}/publish", summary="正式发布文章")
async def publish_article(article_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Article).where(Article.id == article_id))
    article = res.scalars().first()
    if not article or (article.user_id != user.id and user.role != UserRole.ADMIN):
        raise HTTPException(status_code=403)
    article.status, article.published_at, article.is_audited = ArticleStatus.PUBLISHED, datetime.now(), False
    await db.commit()
    return {"message": "已发布"}