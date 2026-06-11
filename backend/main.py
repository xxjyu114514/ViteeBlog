import uvicorn
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from core.database import init_db, IS_LITE, IS_DEMO
from routers.v1 import api_auth, api_article,api_meta,api_comment,api_favorite,api_channel,api_social,api_user
from fastapi.staticfiles import StaticFiles
from middleware.log_middleware import LogMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时初始化数据库"""
    await init_db()
    mode = "Demo (公网演示)" if IS_DEMO else "Lite (本地开发)" if IS_LITE else "Production (MySQL)"
    print(f">>> ViteeBlog 启动成功 | 当前模式: {mode}")
    yield
    # 关闭时的清理逻辑可放在 yield 之后


def create_app() -> FastAPI:
    app = FastAPI(
        title="ViteeBlog API",
        description="基于 FastAPI 的个人博客后端系统",
        version="1.0.0",
        lifespan=lifespan
    )

    # 1. 添加日志中间件（最先执行）
    app.add_middleware(LogMiddleware)

    # 2. 配置 CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 3. 注册路由
    app.include_router(api_auth.router, prefix="/api/v1/auth", tags=["认证管理"])
    app.include_router(api_article.router, prefix="/api/v1/article", tags=["文章业务"])
    app.include_router(api_meta.router, prefix="/api/v1/meta", tags=["分类与标签管理"])
    app.include_router(api_comment.router, prefix="/api/v1/comments", tags=["评论管理"])
    app.include_router(api_favorite.router, prefix="/api/v1/favorites", tags=["文章收藏"])  # 已新增
    app.include_router(api_channel.router, prefix="/api/v1/channels", tags=["频道广场聊天系统"])
    app.include_router(api_social.router, prefix="/api/v1/social", tags=["社交关注"])
    app.include_router(api_user.router, prefix="/api/v1/users", tags=["用户主页"])

    # 4. 挂载静态文件目录
    app.mount("/storage", StaticFiles(directory="storage"), name="storage")

    @app.get("/", tags=["Root"])
    async def root():
        return {"message": "Welcome to ViteeBlog API", "status": "running", "lite_mode": IS_LITE}

    return app


app = create_app()

if __name__ == "__main__":
    # 支持命令行参数启动
    # -lite : SQLite 快速开发模式 (127.0.0.1)
    # -demo : SQLite 演示模式 + 绑定 0.0.0.0 (公网可访问)
    host = "0.0.0.0" if IS_DEMO else "127.0.0.1"
    port = 8000
    mode_label = "Demo (公网演示)" if IS_DEMO else "Lite (本地开发)" if IS_LITE else "Production (MySQL)"

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=False  ## 演示/Lite 模式下关闭 reload 避免异常退出
    )
    print(f">>> ViteeBlog 已停止 | 模式: {mode_label}")
