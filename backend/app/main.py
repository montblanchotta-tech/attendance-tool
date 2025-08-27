"""
勤怠管理システム - メインアプリケーション
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.database import engine
from .models import Base
from .routers import auth, attendance, admin, corrections, reports

# データベーステーブル作成
Base.metadata.create_all(bind=engine)

# FastAPIアプリケーション
app = FastAPI(title="勤怠管理システム", version="1.0.0")

# CORS設定 - 環境変数から許可するオリジンを取得
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーター登録
app.include_router(auth.router)
app.include_router(attendance.router)
app.include_router(admin.router)
app.include_router(corrections.router)
app.include_router(reports.router)

@app.get("/")
def read_root():
    return {"message": "勤怠管理システムAPI"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)