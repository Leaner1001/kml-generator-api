from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db
from app.api import auth, user, upload, kml


# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    description="图层生成工具API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(upload.router)
app.include_router(kml.router)


@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    # 初始化数据库
    await init_db()
    print("数据库初始化完成")


@app.get("/", summary="健康检查")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "message": "图层生成工具API服务运行正常"
    }


@app.get("/api", summary="API根路径")
async def api_root():
    """API根路径"""
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "endpoints": {
            "auth": "/api/auth",
            "user": "/api/user",
            "upload": "/api/upload",
            "kml": "/api/kml"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
