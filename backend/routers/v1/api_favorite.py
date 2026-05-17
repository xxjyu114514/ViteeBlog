import math
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError

from dependencies import get_db, get_current_user
from models.blog_models import User, Article, ArticleFavorite, ArticleStatus
from schemas.favorite_schema import FavoriteResponse, ArticleSimpleOut

router = APIRouter()


@router.post("/{article_id}/favorite", summary="收藏或取消收藏文章")
async def toggle_favorite(
        article_id: int,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    # 1. 校验文章状态
    res = await db.execute(select(Article).where(Article.id == article_id))
    article = res.scalars().first()
    if not article or article.status != ArticleStatus.PUBLISHED or article.deleted_at is not None:
        raise HTTPException(status_code=404, detail="文章不存在或未公开发布")

    # 2. 检查收藏状态
    stmt = select(ArticleFavorite).where(
        ArticleFavorite.user_id == user.id,
        ArticleFavorite.article_id == article_id
    )
    fav_res = await db.execute(stmt)
    favorite = fav_res.scalars().first()

    if favorite:
        # 已收藏则取消
        await db.delete(favorite)
        await db.commit()
        return {"favorited": False, "message": "已取消收藏"}
    else:
        # 未收藏则新增
        new_fav = ArticleFavorite(user_id=user.id, article_id=article_id)
        db.add(new_fav)
        try:
            await db.commit()
            return {"favorited": True, "message": "收藏成功"}
        except IntegrityError:
            await db.rollback()
            return {"favorited": True, "message": "已收藏"}


@router.get("/my", response_model=dict, summary="获取我的收藏列表")
async def get_my_favorites(
        page: int = Query(1, ge=1),
        size: int = Query(10, ge=1),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    # 构建查询语句并预加载文章信息
    stmt = (
        select(ArticleFavorite)
        .where(ArticleFavorite.user_id == user.id)
        .options(selectinload(ArticleFavorite.article))
        .order_by(ArticleFavorite.created_at.desc())
    )

    # 获取总数
    total_res = await db.execute(select(func.count()).select_from(stmt.subquery()))
    total = total_res.scalar() or 0

    # 分页查询
    res = await db.execute(stmt.offset((page - 1) * size).limit(size))
    items = res.scalars().all()

    # 将 ORM 对象转换为 Pydantic 模型
    favorite_responses = []
    for fav in items:
        favorite_responses.append(FavoriteResponse.model_validate(fav))

    return {
        "items": favorite_responses,
        "total": total,
        "page": page,
        "size": size,
        "pages": math.ceil(total / size)
    }


@router.get("/check/{article_id}", summary="检查当前用户是否收藏了该文章")
async def check_favorite(
        article_id: int,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    stmt = select(ArticleFavorite).where(
        ArticleFavorite.user_id == user.id,
        ArticleFavorite.article_id == article_id
    )
    res = await db.execute(stmt)
    is_favorited = res.scalars().first() is not None
    return {"favorited": is_favorited}

