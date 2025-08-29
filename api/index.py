"""
Vercel用エントリーポイント
"""
import sys
import os
from pathlib import Path

# backendディレクトリをPythonパスに追加
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# 環境変数設定
os.environ["DATABASE_URL"] = os.getenv("DATABASE_URL", "sqlite:///./attendance.db")
os.environ["SECRET_KEY"] = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
os.environ["ALLOWED_ORIGINS"] = os.getenv("ALLOWED_ORIGINS", "*")

# ログ設定を簡素化（Vercel環境用）
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

try:
    # FastAPIアプリケーションをインポート
    from app.main import app
    
    # Vercelが認識するために必要
    handler = app
    
    # デバッグ情報
    logging.info("Vercel API handler initialized successfully")
    
except Exception as e:
    logging.error(f"Failed to initialize Vercel handler: {e}", exc_info=True)
    
    # エラー時の簡易ハンドラー
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    app = FastAPI()
    
    @app.get("/api/{path:path}")
    @app.post("/api/{path:path}")
    @app.put("/api/{path:path}")
    @app.delete("/api/{path:path}")
    async def error_handler(path: str):
        return JSONResponse(
            status_code=500,
            content={"detail": f"サーバー初期化エラー: {str(e)}"}
        )
    
    handler = app