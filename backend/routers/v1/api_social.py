import traceback
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, exists
from dependencies import get_db, get_current_user, get_current_user_optional
from models.blog_models import User, UserFollow
from schemas.social_schema import UserSocialOut, SocialPaginationOut

router = APIRouter(tags=["社交关注"])

@router.post("/follow/{user_id}", summary="关注用户")
async def follow_user(
    user_id: int, 
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="你不能关注你自己")

    try:
        # 1. 检查是否已经关注过
        is_followed_stmt = select(exists().where(
            UserFollow.follower_id == current_user.id,
            UserFollow.followed_id == user_id
        ))
        is_followed = (await db.execute(is_followed_stmt)).scalar()
        
        if is_followed:
            return {"message": "你已经关注了该用户"}

        # 2. 检查目标用户是否存在
        res = await db.execute(select(User).where(User.id == user_id, User.is_active == True))
        target_user = res.scalars().first()
        if not target_user:
            raise HTTPException(status_code=404, detail="目标用户不存在或已注销")

        # 3. 执行关注操作
        new_follow = UserFollow(follower_id=current_user.id, followed_id=user_id)
        db.add(new_follow)
        
        current_user.following_count += 1
        target_user.followers_count += 1
        
        await db.commit()
        return {"message": "关注成功"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="关注操作失败")


@router.delete("/follow/{user_id}", summary="取消关注")
async def unfollow_user(
    user_id: int, 
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    try:
        # 优化查询：一次性获取关系和目标用户
        stmt = (
            select(UserFollow, User)
            .join(User, UserFollow.followed_id == User.id)
            .where(UserFollow.follower_id == current_user.id)
            .where(UserFollow.followed_id == user_id)
        )
        result = (await db.execute(stmt)).first()
        
        if not result:
            raise HTTPException(status_code=400, detail="你尚未关注该用户")

        follow_rel, target_user = result
        
        await db.delete(follow_rel)
        current_user.following_count = max(0, current_user.following_count - 1)
        target_user.followers_count = max(0, target_user.followers_count - 1)
        
        await db.commit()
        return {"message": "已取消关注"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="取消关注失败")


@router.get("/following/{user_id}", response_model=SocialPaginationOut, summary="获取某人的关注列表")
async def get_following(
    user_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    # 查询关注列表
    stmt = (
        select(User)
        .join(UserFollow, User.id == UserFollow.followed_id)
        .where(UserFollow.follower_id == user_id)
        .offset((page - 1) * size)
        .limit(size)
    )
    count_stmt = select(func.count()).select_from(UserFollow).where(UserFollow.follower_id == user_id)
    
    users_res = await db.execute(stmt)
    total_res = await db.execute(count_stmt)
    
    users = users_res.scalars().all()
    total = total_res.scalar() or 0

    # 处理 is_following 逻辑
    items = []
    following_ids = set()
    target_ids = [u.id for u in users]

    # 关键修复：增加 target_ids 判空，防止 SQL 报错
    if current_user and target_ids:
        check_stmt = select(UserFollow.followed_id).where(
            UserFollow.follower_id == current_user.id,
            UserFollow.followed_id.in_(target_ids)
        )
        following_res = await db.execute(check_stmt)
        following_ids = set(following_res.scalars().all())

    for u in users:
        user_out = UserSocialOut.model_validate(u)
        user_out.is_following = u.id in following_ids
        items.append(user_out)

    return {"total": total, "items": items}


@router.get("/followers/{user_id}", response_model=SocialPaginationOut, summary="获取某人的粉丝列表")
async def get_followers(
    user_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    # 查询粉丝列表
    stmt = (
        select(User)
        .join(UserFollow, User.id == UserFollow.follower_id)
        .where(UserFollow.followed_id == user_id)
        .offset((page - 1) * size)
        .limit(size)
    )
    count_stmt = select(func.count()).select_from(UserFollow).where(UserFollow.followed_id == user_id)
    
    users_res = await db.execute(stmt)
    total_res = await db.execute(count_stmt)
    
    users = users_res.scalars().all()
    total = total_res.scalar() or 0

    # 处理 is_following 逻辑（当前用户是否关注了这些粉丝）
    items = []
    following_ids = set()
    target_ids = [u.id for u in users]

    # 关键修复：增加 target_ids 判空
    if current_user and target_ids:
        check_stmt = select(UserFollow.followed_id).where(
            UserFollow.follower_id == current_user.id,
            UserFollow.followed_id.in_(target_ids)
        )
        following_res = await db.execute(check_stmt)
        following_ids = set(following_res.scalars().all())

    for u in users:
        user_out = UserSocialOut.model_validate(u)
        user_out.is_following = u.id in following_ids
        items.append(user_out)

    return {"total": total, "items": items}
