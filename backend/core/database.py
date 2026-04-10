from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import QueuePool
from core.config import settings

# 1. 创建异步引擎 [cite: 5, 25-30]
# 使用 aiomysql 驱动，并配置工业级连接池
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,                # 生产环境建议关闭 SQL 日志以提高性能
    # poolclass=QueuePool,       # 使用连接池管理
    pool_size=10,              # 基础连接数
    max_overflow=20,           # 允许临时溢出的最大连接数
    pool_recycle=3600,         # 连接回收时间（秒），防止 MySQL 8.0 的 8小时断开问题
    pool_pre_ping=True,        # 每次从池中取连接先检查是否可用
)

# 2. 创建异步会话工厂
# expire_on_commit=False 是异步开发的关键，防止提交后无法访问对象属性
async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)

# 3. 数据库初始化函数（可选，之后主要靠 Alembic）
async def init_db():
    from models.base import Base
    # 注意：这里导入 models 必须放在函数内部，防止循环导入
    from models import blog_models
    async with engine.begin() as conn:
        # 仅用于开发环境快速建表，生产环境严禁使用此行
        # await conn.run_sync(Base.metadata.create_all)
        pass