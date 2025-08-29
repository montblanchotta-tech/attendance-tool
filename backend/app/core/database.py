"""
データベース設定とセッション管理
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from .config import settings

# Vercel環境でのSQLiteファイルパス調整
database_url = settings.DATABASE_URL
if "sqlite" in database_url and os.getenv("VERCEL"):
    # Vercelの書き込み可能ディレクトリを使用
    database_url = "sqlite:////tmp/attendance.db"

# SQLAlchemy エンジン作成
engine = create_engine(
    database_url,
    connect_args={"check_same_thread": False} if "sqlite" in database_url else {}
)

# セッションファクトリ
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ベースクラス
Base = declarative_base()

def get_db() -> Session:
    """データベースセッションの依存性注入"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """全テーブルを作成"""
    Base.metadata.create_all(bind=engine)