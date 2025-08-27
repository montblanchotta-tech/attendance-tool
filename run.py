#!/usr/bin/env python
"""
統合サーバー起動スクリプト
フロントエンドとバックエンドを1つのポートで提供
"""
import sys
import os
from pathlib import Path

# backendディレクトリをPythonパスに追加
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

if __name__ == "__main__":
    import uvicorn
    from app.main import app
    
    # ネットワークからのアクセスを許可
    host = "0.0.0.0"
    port = int(os.getenv("PORT", 8001))
    
    print("="*50)
    print("勤怠管理システム - 統合サーバー")
    print("="*50)
    print(f"サーバー起動中...")
    print(f"アクセスURL:")
    print(f"  http://localhost:{port}")
    
    # IPアドレスも表示
    import socket
    hostname = socket.gethostname()
    try:
        ip = socket.gethostbyname(hostname)
        print(f"  http://{ip}:{port}")
    except:
        pass
    
    print("="*50)
    print("Ctrl+C で停止")
    print("")
    
    # サーバー起動
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )