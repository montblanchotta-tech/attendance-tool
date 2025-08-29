"""
勤怠管理システム - メインアプリケーション
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.database import engine
from .models import Base
from .routers import auth, attendance, admin, corrections, reports

# データベーステーブル作成
Base.metadata.create_all(bind=engine)

# FastAPIアプリケーション
app = FastAPI(title="勤怠管理システム", version="1.0.0")

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    uvicorn.run(app, host="0.0.0.0", port=8001)