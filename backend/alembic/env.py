import asyncio
from logging.config import fileConfig
from os.path import abspath, dirname
import sys

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

# --- 严谨的路径处理 ---
# 确保项目根目录被加入 sys.path，这样才能正确导入 core 和 models 软件包
ROOT_DIR = dirname(dirname(abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from core.config import settings
from models.base import Base
from models import blog_models  # 必须导入以加载模型

# Alembic 配置对象
config = context.config

# 配置日志
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 目标元数据，用于 autogenerate 自动生成迁移脚本
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """离线模式迁移：直接生成 SQL 脚本而不需要连接数据库"""
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    """同步执行迁移的具体逻辑（被 run_sync 调用）"""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        render_as_batch=True  # 启用批处理模式，增强对数据库约束修改的支持
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    """在线模式迁移：使用异步引擎连接数据库"""
    # 直接使用 settings 中的异步连接字符串
    connectable = create_async_engine(
        settings.DATABASE_URL,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        # 核心桥接：在异步连接中同步运行迁移逻辑
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

# --- 入口逻辑 ---
if context.is_offline_mode():
    run_migrations_offline()
else:
    try:
        # 使用 asyncio 驱动异步在线迁移
        asyncio.run(run_migrations_online())
    except (KeyboardInterrupt, SystemExit):
        pass