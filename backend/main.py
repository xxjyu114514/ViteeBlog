import uvicorn
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from core.database import init_db, IS_LITE
from routers.v1 import api_auth, api_article, api_meta
from fastapi.staticfiles import StaticFiles


def create_app() -> FastAPI:
    app = FastAPI(
        title="ViteeBlog API",
        description="基于 FastAPI 的个人博客后端系统",
        version="1.0.0"
    )

    # 1. 配置 CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 2. 生命周期事件：启动时初始化数据库
    @app.on_event("startup")
    async def startup_event():
        await init_db()
        mode = "SQLite (Lite)" if IS_LITE else "MySQL (Production)"
        print(f">>> ViteeBlog 启动成功 | 当前模式: {mode}")

    # 3. 注册路由
    app.include_router(api_auth.router, prefix="/api/v1/auth", tags=["认证管理"])
    app.include_router(api_article.router, prefix="/api/v1/article", tags=["文章业务"])
    app.include_router(api_meta.router, prefix="/api/v1/meta", tags=["分类与标签管理"])

    # 4. 挂载静态文件目录
    app.mount("/storage", StaticFiles(directory="storage"), name="storage")

    @app.get("/", tags=["Root"])
    async def root():
        return {"message": "Welcome to ViteeBlog API", "status": "running", "lite_mode": IS_LITE}

    return app


app = create_app()

if __name__ == "__main__":
    # 支持命令行参数启动
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True if not IS_LITE else False  # Lite 模式通常用于临时测试，可根据需要调整 reload
    )