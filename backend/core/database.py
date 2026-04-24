import sys
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import event
from core.config import settings

# 1. 识别启动参数：检查是否包含 -lite
IS_LITE = "-lite" in sys.argv

# 2. 根据模式创建异步引擎
if IS_LITE:
    # SQLite 异步连接字符串
    DATABASE_URL = "sqlite+aiosqlite:///./viteeblog_lite.db"
    engine = create_async_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},  # SQLite 异步必须配置
        echo=False
    )


    # 兼容性补丁：强制开启 SQLite 的外键约束
    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
else:
    # 保留原有的 MySQL 工业级配置
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_size=10,
        max_overflow=20,
        pool_recycle=3600,
        pool_pre_ping=True,
    )

# 3. 创建异步会话工厂
async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)


# 4. 数据库初始化函数
async def init_db():
    from models.base import Base
    from models import blog_models  # 防止循环导入
    async with engine.begin() as conn:
        # 在 Lite 模式下自动创建所有表，方便前端快速测试
        if IS_LITE:
            await conn.run_sync(Base.metadata.create_all)