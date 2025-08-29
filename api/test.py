"""
Vercel API テストエンドポイント
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import sys
import os
from pathlib import Path

# backendディレクトリをPythonパスに追加
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

app = FastAPI()

@app.get("/api/test")
async def test_endpoint():
    """テストエンドポイント - 環境情報を返す"""
    return JSONResponse(
        status_code=200,
        content={
            "status": "ok",
            "message": "API is working",
            "python_version": sys.version,
            "backend_path": str(backend_path),
            "environment": {
                "VERCEL": os.getenv("VERCEL", "Not in Vercel"),
                "DATABASE_URL": os.getenv("DATABASE_URL", "Not set"),
                "SECRET_KEY": "Set" if os.getenv("SECRET_KEY") else "Not set",
            },
            "modules": list(sys.modules.keys())[:10]  # 最初の10モジュール
        }
    )

handler = app