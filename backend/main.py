import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from routers.v1 import api_auth, api_article  # 预导入路由模块
from fastapi.staticfiles import StaticFiles #挂载文章和图片路径的静态目录

def create_app() -> FastAPI:
    """
    创建并配置 FastAPI 实例
    """
    app = FastAPI(
        title="ViteeBlog API",
        description="基于 FastAPI 的个人博客后端系统",
        version="1.0.0"
    )

    # 1. 配置 CORS 跨域（严谨对接前端 ViteeBlog）
    # 在开发阶段允许所有来源，生产环境应从 settings 中读取具体域名
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 允许前端 Vite 默认端口或所有来源
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 2. 注册路由
    app.include_router(api_auth.router, prefix="/api/v1/auth", tags=["认证管理"])
    app.include_router(api_article.router, prefix="/api/v1/article", tags=["文章管理"])
    
    # 3. 挂载静态文件目录
    app.mount("/static/storage", StaticFiles(directory="storage"), name="static_storage")
    
    @app.get("/", tags=["Root"])
    async def root():
        return {"message": "Welcome to ViteeBlog API", "status": "running"}

    return app

app = create_app()

if __name__ == "__main__":
    # 严谨配置：使用 uvicorn 启动
    uvicorn.run(
        "main:app",
        host="127.0.0.1", 
        port=8000, 
        reload=True  # 开发模式自动重载
    )