from typing import AsyncGenerator
from core.database import async_session_maker
from sqlalchemy.ext.asyncio import AsyncSession

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI 依赖注入函数：
    确保每个请求拥有独立的数据库会话，并在请求结束时自动关闭连接。
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()