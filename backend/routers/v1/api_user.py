import math
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from dependencies import get_db, get_current_user_optional
from models.blog_models import User, Article, ArticleStatus, UserFollow, ArticleLike, ArticleFavorite, Comment
from schemas.user_schema import UserProfileOut, ArticleSimpleOut

router = APIRouter(tags=["用户主页"])


@router.get("/{user_id}", response_model=UserProfileOut, summary="获取用户个人主页信息")
async def get_user_profile(
    user_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    获取指定用户的个人主页信息（公开接口）
    - 返回用户基本信息、关注数、粉丝数等
    - 如果当前用户已登录，会返回 is_following 状态
    - 包含统计数据：文章总数、总点赞数、总阅读量、最后活跃时间
    """
    # 查询目标用户
    res = await db.execute(select(User).where(User.id == user_id, User.is_active == True))
    target_user = res.scalars().first()
    
    if not target_user:
        raise HTTPException(status_code=404, detail="用户不存在或已注销")
    
    # 构建响应对象
    profile = UserProfileOut.model_validate(target_user)
    
    # 如果当前用户已登录，查询是否关注了目标用户
    if current_user:
        follow_check = await db.execute(
            select(UserFollow).where(
                UserFollow.follower_id == current_user.id,
                UserFollow.followed_id == user_id
            )
        )
        profile.is_following = follow_check.scalars().first() is not None
    else:
        profile.is_following = False
    
    # 计算统计数据
    # 1. 文章总数
    article_count_stmt = select(func.count(Article.id)).where(
        Article.user_id == user_id,
        Article.status == ArticleStatus.PUBLISHED,
        Article.deleted_at == None
    )
    profile.total_articles = (await db.execute(article_count_stmt)).scalar() or 0
    
    # 2. 总点赞数（该用户所有文章获得的点赞总数）
    likes_stmt = select(func.count(ArticleLike.id)).join(
        Article, ArticleLike.article_id == Article.id
    ).where(
        Article.user_id == user_id,
        Article.status == ArticleStatus.PUBLISHED,
        Article.deleted_at == None
    )
    profile.total_likes_received = (await db.execute(likes_stmt)).scalar() or 0
    
    # 3. 总阅读量（该用户所有文章的浏览量总和）
    views_stmt = select(func.sum(Article.view_count)).where(
        Article.user_id == user_id,
        Article.status == ArticleStatus.PUBLISHED,
        Article.deleted_at == None
    )
    profile.total_views = (await db.execute(views_stmt)).scalar() or 0
    
    # 4. 最后活跃时间（最新文章的发布时间）
    last_active_stmt = select(func.max(Article.published_at)).where(
        Article.user_id == user_id,
        Article.status == ArticleStatus.PUBLISHED,
        Article.deleted_at == None
    )
    profile.last_active_at = (await db.execute(last_active_stmt)).scalar()
    
    # 5. 总收藏数（该用户所有文章被收藏的总次数）
    favorites_stmt = select(func.count(ArticleFavorite.id)).join(
        Article, ArticleFavorite.article_id == Article.id
    ).where(
        Article.user_id == user_id,
        Article.status == ArticleStatus.PUBLISHED,
        Article.deleted_at == None
    )
    profile.total_favorites = (await db.execute(favorites_stmt)).scalar() or 0
    
    # 6. 总评论数（该用户所有文章收到的评论总数）
    comments_stmt = select(func.count(Comment.id)).join(
        Article, Comment.article_id == Article.id
    ).where(
        Article.user_id == user_id,
        Article.status == ArticleStatus.PUBLISHED,
        Article.deleted_at == None,
        Comment.is_audited == True  # 只统计已审核通过的评论
    )
    profile.total_comments = (await db.execute(comments_stmt)).scalar() or 0
    
    return profile


@router.get("/{user_id}/articles", summary="获取该用户发布的文章列表")
async def get_user_articles(
    user_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """
    获取指定用户发布的所有公开文章（分页）
    - 只返回 status=PUBLISHED 且 deleted_at IS NULL 的文章
    - 按 created_at 倒序排列
    - 预加载 tags 关系
    """
    # 验证用户是否存在
    user_res = await db.execute(select(User).where(User.id == user_id, User.is_active == True))
    if not user_res.scalars().first():
        raise HTTPException(status_code=404, detail="用户不存在或已注销")
    
    # 构建查询条件
    filters = [
        Article.user_id == user_id,
        Article.status == ArticleStatus.PUBLISHED,
        Article.deleted_at == None
    ]
    
    # 查询总数
    count_stmt = select(func.count(Article.id)).where(and_(*filters))
    total_res = await db.execute(count_stmt)
    total = total_res.scalar() or 0
    
    # 查询文章列表（分页 + 预加载 tags）
    query = (
        select(Article)
        .where(and_(*filters))
        .options(selectinload(Article.tags))
        .order_by(Article.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    
    articles_res = await db.execute(query)
    articles = articles_res.scalars().all()
    
    # 转换为简化输出格式
    items = []
    for article in articles:
        item = ArticleSimpleOut.model_validate(article)
        items.append(item)
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
        "pages": math.ceil(total / size) if total > 0 else 0
    }
