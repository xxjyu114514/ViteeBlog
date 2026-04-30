import jwt
from typing import AsyncGenerator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import async_session_maker
from core.config import settings
from models.blog_models import User, UserRole

# 1. 修改 oauth2_scheme，允许手动处理错误
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login", auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    # 2. 开头增加 token 为空的处理
    if not token:
        raise HTTPException(status_code=401, detail="请先登录")

    try:
        # 使用配置文件中的 SECRET_KEY 进行解码
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="无效的认证凭据")
    except Exception:
        raise HTTPException(status_code=401, detail="登录已过期或凭据错误")

    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user


async def allow_admin_only(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="权限不足，仅限管理员操作")
    return current_user


# 3. 新增 get_current_user_optional 函数
async def get_current_user_optional(
        token: Optional[str] = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    可选的登录校验：
    - 如果未提供 token，返回 None
    - 如果 token 校验失败，返回 None
    - 如果校验成功且用户存在，返回 User 对象
    """
    if not token:
        return None

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None

        result = await db.execute(select(User).where(User.id == int(user_id)))
        return result.scalars().first()
    except Exception:
        # 解析失败不抛出异常，直接返回 None
        return None
    ##