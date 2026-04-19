import jwt
from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import async_session_maker
from models.blog_models import User, UserRole

# 对应 api_auth.py 中的登录地址
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """确保每个请求拥有独立的数据库会话 """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    """
    验证用户 Token 并返回用户对象。
    使用了你在 .env 中定义的 SECRET_KEY: whdagm1966
    """
    try:
        # 解码 Token
        payload = jwt.decode(token, "whdagm1966", algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="无效的认证凭据")
    except Exception:
        raise HTTPException(status_code=401, detail="登录已过期或凭据错误")

    # 查询数据库获取最新用户信息
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user

def allow_blogger_only(current_user: User = Depends(get_current_user)):
    """权限拦截器：强制要求博主权限 (ADMIN) """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="权限不足：只有博主可以执行此操作")
    return current_user