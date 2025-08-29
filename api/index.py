"""
Vercel用エントリーポイント - 簡略版
"""
from http.server import BaseHTTPRequestHandler
import json
import sqlite3
import hashlib
import os
from datetime import datetime

# データベース初期化
def init_db():
    db_path = "/tmp/attendance.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # ユーザーテーブル
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            is_admin BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 勤怠記録テーブル
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date DATE NOT NULL,
            clock_in TIMESTAMP,
            clock_out TIMESTAMP,
            break_start TIMESTAMP,
            break_end TIMESTAMP,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# パスワードハッシュ化
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# JSONレスポンス送信
def send_json_response(handler, status_code, data):
    handler.send_response(status_code)
    handler.send_header('Content-Type', 'application/json')
    handler.send_header('Access-Control-Allow-Origin', '*')
    handler.send_header('Access-Control-Allow-Credentials', 'true')
    handler.end_headers()
    handler.wfile.write(json.dumps(data).encode())

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.end_headers()
    
    def do_GET(self):
        if self.path == '/api/health':
            send_json_response(self, 200, {"status": "healthy", "timestamp": datetime.now().isoformat()})
        else:
            send_json_response(self, 200, {"message": "API is working", "path": self.path})
    
    def do_POST(self):
        try:
            # データベース初期化
            init_db()
            
            # リクエストボディを読み取る
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            if not post_data:
                send_json_response(self, 400, {"detail": "リクエストボディが空です"})
                return
            
            try:
                data = json.loads(post_data)
            except json.JSONDecodeError:
                send_json_response(self, 400, {"detail": "無効なJSON形式です"})
                return
            
            # ログインエンドポイント
            if self.path == '/api/auth/login':
                username = data.get('username')
                password = data.get('password')
                
                if not username or not password:
                    send_json_response(self, 400, {"detail": "ユーザー名とパスワードが必要です"})
                    return
                
                # データベースからユーザーを検索
                conn = sqlite3.connect("/tmp/attendance.db")
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, username, email, full_name, is_admin FROM users WHERE username = ? AND hashed_password = ?",
                    (username, hash_password(password))
                )
                user = cursor.fetchone()
                conn.close()
                
                if user:
                    response = {
                        "access_token": "dummy_token_" + str(user[0]),
                        "token_type": "bearer",
                        "user": {
                            "id": user[0],
                            "username": user[1],
                            "email": user[2],
                            "full_name": user[3],
                            "is_admin": bool(user[4]),
                            "created_at": datetime.now().isoformat()
                        }
                    }
                    send_json_response(self, 200, response)
                else:
                    send_json_response(self, 401, {"detail": "ユーザー名またはパスワードが間違っています"})
            
            # 新規登録エンドポイント
            elif self.path == '/api/auth/register':
                username = data.get('username')
                email = data.get('email')
                password = data.get('password')
                full_name = data.get('full_name')
                
                if not all([username, email, password, full_name]):
                    send_json_response(self, 400, {"detail": "すべてのフィールドが必要です"})
                    return
                
                conn = sqlite3.connect("/tmp/attendance.db")
                cursor = conn.cursor()
                
                try:
                    cursor.execute(
                        "INSERT INTO users (username, email, hashed_password, full_name) VALUES (?, ?, ?, ?)",
                        (username, email, hash_password(password), full_name)
                    )
                    conn.commit()
                    user_id = cursor.lastrowid
                    send_json_response(self, 200, {"message": "ユーザー登録が完了しました", "user_id": user_id})
                except sqlite3.IntegrityError:
                    send_json_response(self, 400, {"detail": "ユーザー名またはメールアドレスが既に使用されています"})
                finally:
                    conn.close()
            
            else:
                send_json_response(self, 404, {"detail": "エンドポイントが見つかりません"})
                
        except Exception as e:
            send_json_response(self, 500, {"detail": f"サーバーエラー: {str(e)}"})