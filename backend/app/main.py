"""
勤怠管理システム - メインアプリケーション
"""
import os
import logging
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .core.database import engine
from .models import Base
from .routers import auth, attendance, admin, corrections, reports

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# データベーステーブル作成
Base.metadata.create_all(bind=engine)

# FastAPIアプリケーション
app = FastAPI(title="勤怠管理システム", version="1.0.0")

# CORS設定 - 環境変数から許可するオリジンを取得
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")

# 開発環境用のオリジンも追加
if "*" not in allowed_origins:
    allowed_origins.extend([
        "http://localhost:8000",
        "http://localhost:8001",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:8001",
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if "*" not in allowed_origins else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# エラーハンドラー
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc.detail)}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation Error: {exc}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"General Exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "内部サーバーエラーが発生しました。"}
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
    # ルートパスでindex.htmlを返す
    @app.get("/")
    async def read_index():
        return FileResponse(str(frontend_path / "index.html"))
    
    # 静的ファイルとSPAルート処理
    @app.get("/{full_path:path}")
    async def serve_static_or_spa(full_path: str):
        # APIパスは除外
        if full_path.startswith("api/"):
            return {"message": "API endpoint not found"}
        
        # ファイルパスを構築
        file_path = frontend_path / full_path
        
        # ファイルが存在する場合はそのまま返す
        if file_path.exists() and file_path.is_file():
            # MIMEタイプを適切に設定
            if full_path.endswith('.css'):
                return FileResponse(str(file_path), media_type="text/css")
            elif full_path.endswith('.js'):
                return FileResponse(str(file_path), media_type="application/javascript")
            elif full_path.endswith('.html'):
                return FileResponse(str(file_path), media_type="text/html")
            else:
                return FileResponse(str(file_path))
        
        # それ以外はindex.htmlを返す（SPA対応）
        return FileResponse(str(frontend_path / "index.html"))
else:
    @app.get("/")
    def read_root():
        return {"message": "勤怠管理システムAPI"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)