"""
アプリケーション設定
"""
import os
from typing import Optional

class Settings:
    # データベース設定
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./attendance.db")
    
    # JWT設定
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS設定
    ALLOWED_ORIGINS: list = ["*"]  # 本番環境では具体的なドメインを指定
    
    # アプリケーション設定
    APP_NAME: str = "勤怠管理システム"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # サーバー設定
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8001"))
    
    class Config:
        env_file = ".env"

settings = Settings()