import os
import time
import aiofiles
import traceback
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, Body, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_
from sqlalchemy.orm import selectinload
from dependencies import get_db, allow_blogger_only, get_current_user
from models.blog_models import Article, ArticleStatus, User, Category, Tag

router = APIRouter()

# 存储配置
STORAGE_BASE = "storage/articles"


@router.post("/autosave", summary="自动保存/实时更新（博主权限）")
async def autosave_article(
        title: str = Body(...),
        content: str = Body(...),
        article_id: Optional[int] = Body(None),
        category_id: Optional[int] = Body(None),
        tag_ids: List[int] = Body([], description="标签ID列表"),
        user: User = Depends(allow_blogger_only),
        db: AsyncSession = Depends(get_db)
):
    try:
        article = None
        if article_id:
            res = await db.execute(
                select(Article)
                .options(selectinload(Article.tags))
                .where(Article.id == article_id)
            )
            article = res.scalars().first()
            if not article or article.user_id != user.id:
                raise HTTPException(status_code=403, detail="无权操作此文章")
            file_path = article.content_path
        else:
            os.makedirs(STORAGE_BASE, exist_ok=True)
            filename = f"user{user.id}_{int(time.time())}.md"
            file_path = os.path.join(STORAGE_BASE, filename)

        async with aiofiles.open(file_path, mode='w', encoding='utf-8') as f:
            await f.write(content)

        if not article_id:
            article = Article(
                title=title,
                summary=content[:200].replace("#", "").strip(),
                content_path=file_path,
                user_id=user.id,
                category_id=category_id,
                status=ArticleStatus.DRAFT
            )
            if tag_ids:
                tag_res = await db.execute(select(Tag).where(Tag.id.in_(tag_ids)))
                article.tags = list(tag_res.scalars().all())
            db.add(article)
        else:
            article.title = title
            article.category_id = category_id
            if tag_ids is not None:
                tag_res = await db.execute(select(Tag).where(Tag.id.in_(tag_ids)))
                article.tags = list(tag_res.scalars().all())

        await db.commit()
        if not article_id:
            await db.refresh(article)

        relative_url = file_path.replace("\\", "/")
        return {"article_id": article.id, "url": f"/static/{relative_url}", "message": "内容已同步"}
    except Exception as e:
        await db.rollback()
        print(f"❌ [ArticleAPI] 保存失败: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="保存失败")


@router.get("/{article_id}", summary="获取文章详情")
async def get_article_detail(article_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(
        select(Article)
        .options(selectinload(Article.author), selectinload(Article.category), selectinload(Article.tags))
        .where(Article.id == article_id, Article.deleted_at.is_(None))
    )
    article = res.scalars().first()
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")

    content = ""
    if os.path.exists(article.content_path):
        async with aiofiles.open(article.content_path, mode='r', encoding='utf-8') as f:
            content = await f.read()

    article.view_count += 1
    await db.commit()
    return {"info": article, "content": content}


# --- 回收站机制相关接口 ---

@router.delete("/{article_id}", summary="移至回收站（软删除）")
async def soft_delete_article(
        article_id: int,
        user: User = Depends(allow_blogger_only),
        db: AsyncSession = Depends(get_db)
):
    await db.execute(
        update(Article)
        .where(Article.id == article_id, Article.user_id == user.id)
        .values(deleted_at=datetime.now())
    )
    await db.commit()
    return {"message": "已移至回收站"}


@router.post("/{article_id}/restore", summary="恢复已删除的文章")
async def restore_article(
        article_id: int,
        user: User = Depends(allow_blogger_only),
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        update(Article)
        .where(Article.id == article_id, Article.user_id == user.id)
        .values(deleted_at=None)
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="未找到可恢复的文章")
    await db.commit()
    return {"message": "文章已恢复"}


@router.delete("/{article_id}/hard", summary="彻底删除（手动粉碎）")
async def hard_delete_article(
        article_id: int,
        user: User = Depends(allow_blogger_only),
        db: AsyncSession = Depends(get_db)
):
    """手动粉碎文章：同步删除数据库记录和物理文件"""
    res = await db.execute(select(Article).where(Article.id == article_id, Article.user_id == user.id))
    article = res.scalars().first()
    if not article:
        raise HTTPException(status_code=404, detail="文件不存在")

    # 1. 删除磁盘文件
    if os.path.exists(article.content_path):
        try:
            os.remove(article.content_path)
        except Exception as e:
            print(f"⚠️ 物理文件删除失败: {e}")

    # 2. 删除数据库记录
    await db.delete(article)
    await db.commit()
    return {"message": "文章及其文件已永久从服务器删除"}


@router.get("/recycle-bin/list", summary="回收站列表（含自动清理逻辑）")
async def get_recycle_bin(
        user: User = Depends(allow_blogger_only),
        db: AsyncSession = Depends(get_db)
):
    """
    1. 查询所有已软删除的文章。
    2. 顺便执行“超过30天自动清理”逻辑。
    """
    # 自动清理：删除 30 天前的记录
    expiration_date = datetime.now() - timedelta(days=30)

    # 找出过期文章用于物理删除文件
    expired_res = await db.execute(
        select(Article).where(Article.deleted_at < expiration_date)
    )
    expired_articles = expired_res.scalars().all()
    for art in expired_articles:
        if os.path.exists(art.content_path):
            os.remove(art.content_path)

    # 执行物理删除命令
    await db.execute(delete(Article).where(Article.deleted_at < expiration_date))
    await db.commit()

    # 返回剩余的回收站内容
    res = await db.execute(
        select(Article).where(Article.deleted_at.is_not(None), Article.user_id == user.id)
    )
    return res.scalars().all()


# --- 发布与列表 ---

@router.put("/{article_id}/publish", summary="正式发布文章")
async def publish_article(
        article_id: int,
        user: User = Depends(allow_blogger_only),
        db: AsyncSession = Depends(get_db)
):
    res = await db.execute(select(Article).where(Article.id == article_id))
    article = res.scalars().first()
    if not article or article.user_id != user.id:
        raise HTTPException(status_code=404, detail="文章不存在")

    article.status = ArticleStatus.PUBLISHED
    article.published_at = datetime.now()
    article.deleted_at = None  # 发布时确保不处于回收站状态
    await db.commit()
    return {"message": "文章已发布"}


@router.get("/list/public", summary="前台列表")
async def get_public_articles(category_id: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    stmt = select(Article).where(Article.status == ArticleStatus.PUBLISHED, Article.deleted_at.is_(None))
    if category_id:
        stmt = stmt.where(Article.category_id == category_id)
    stmt = stmt.order_by(Article.published_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()