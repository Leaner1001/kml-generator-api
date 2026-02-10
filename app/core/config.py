from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """应用配置类"""
    # 数据库配置
    DATABASE_URL: str = "sqlite+aiosqlite:///./app.db"
    
    # JWT配置
    SECRET_KEY: str = "dev-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7天
    
    # 短信服务配置
    SMS_API_KEY: str = ""
    SMS_API_SECRET: str = ""
    
    # 文件存储配置
    UPLOAD_DIR: str = "./uploads"
    KML_DIR: str = "./kml"
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    
    # 跨域配置
    CORS_ORIGINS: List[str] = ["*"]
    
    # 应用配置
    APP_NAME: str = "图层生成工具API"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建全局配置实例
settings = Settings()
