"""
Vercel用エントリーポイント
"""
import sys
import os
from pathlib import Path

# backendディレクトリをPythonパスに追加
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# FastAPIアプリケーションをインポート
from app.main import app

# Vercelが認識するために必要
handler = app