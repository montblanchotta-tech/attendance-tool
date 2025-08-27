#!/usr/bin/env python
"""
シンプルな管理者ユーザー作成スクリプト
"""

import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import bcrypt

# メインモジュールからインポート
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from main import User, Base

def hash_password(password: str) -> str:
    """パスワードをハッシュ化"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_admin():
    """管理者ユーザーを作成"""
    # データベース接続
    DATABASE_URL = "sqlite:///./attendance.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 既存の管理者チェック
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if existing_admin:
            print(f"管理者ユーザー 'admin' は既に存在します。")
            return
        
        # 管理者ユーザー作成
        hashed_password = hash_password("admin123")
        
        admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=hashed_password,
            full_name="システム管理者",
            is_admin=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("管理者ユーザーが作成されました！")
        print("   ユーザー名: admin")
        print("   パスワード: admin123")
        print("   氏名: システム管理者")
        print("   管理者権限: はい")
        print()
        print("このユーザーでログインして管理機能を使用できます。")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()