"""
勤怠管理システム - メインアプリケーション
"""
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

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

# APIルーター登録（/api プレフィックス付き）
app.include_router(auth.router, prefix="/api")
app.include_router(attendance.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(corrections.router, prefix="/api")
app.include_router(reports.router, prefix="/api")

# 静的ファイル（フロントエンド）の提供
frontend_path = Path(__file__).parent.parent.parent / "frontend"
if frontend_path.exists():
    # 静的ファイルをマウント
    app.mount("/js", StaticFiles(directory=str(frontend_path / "js")), name="js")
    app.mount("/css", StaticFiles(directory=str(frontend_path)), name="css")
    
    # ルートパスでindex.htmlを返す
    @app.get("/")
    async def read_index():
        return FileResponse(str(frontend_path / "index.html"))
    
    # その他のルートもindex.htmlを返す（SPA対応）
    @app.get("/{full_path:path}")
    async def read_spa_routes(full_path: str):
        # APIパスは除外
        if full_path.startswith("api/"):
            return {"message": "API endpoint not found"}
        
        # ファイルが存在する場合はそのまま返す
        file_path = frontend_path / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        
        # それ以外はindex.htmlを返す
        return FileResponse(str(frontend_path / "index.html"))
else:
    @app.get("/")
    def read_root():
        return {"message": "勤怠管理システムAPI"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)