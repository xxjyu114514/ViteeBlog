import sys
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import event
from core.config import settings

# 1. 识别启动参数
#    -lite : SQLite 快速开发模式 (127.0.0.1)
#    -demo : 线上演示模式，使用 MySQL + 绑定 0.0.0.0 (公网可访问)
IS_DEMO = "-demo" in sys.argv
IS_LITE = "-lite" in sys.argv

# 2. 根据模式创建异步引擎
if IS_LITE:
    # SQLite 异步连接字符串（仅 -lite 模式使用）
    DATABASE_URL = "sqlite+aiosqlite:///./viteeblog_lite.db"
    engine = create_async_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False
    )

    # 兼容性补丁：强制开启 SQLite 的外键约束
    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
else:
    # MySQL 工业级配置（production / demo 都用 MySQL）
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

    # 5. 种子数据：仅在 Lite / Demo 模式下且表为空时填充
    if IS_LITE:
        await seed_demo_data()


async def seed_demo_data():
    """为 Lite / Demo 模式填充默认数据（管理员账号 + 默认频道）"""
    from core.security import get_password_hash
    from models.blog_models import User, Channel
    from sqlalchemy import select, func

    async with async_session_maker() as session:
        # 检查是否已有用户
        result = await session.execute(select(func.count()).select_from(User))
        user_count = result.scalar()

        if user_count == 0:
            demo_admin = User(
                username="admin",
                email="admin@demo.com",
                password=get_password_hash("admin123"),
                role=blog_models.UserRole.SUPER_ADMIN,
                is_active=True,
                bio="Demo 模式默认管理员账号",
            )
            session.add(demo_admin)
            await session.flush()

            # 同时创建默认频道
            channel_exists = await session.execute(
                select(func.count()).select_from(Channel)
            )
            if channel_exists.scalar() == 0:
                session.add(Channel(name="闲聊"))
                session.add(Channel(name="技术讨论"))

            await session.commit()
            print(">>> [种子数据] 已创建默认管理员 (admin / admin123) 和默认频道")
        else:
            print(f">>> [种子数据] 已有 {user_count} 个用户，跳过")