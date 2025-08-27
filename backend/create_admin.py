#!/usr/bin/env python
"""
管理者ユーザー作成スクリプト
初期セットアップ時に管理者ユーザーを作成するためのスクリプトです。
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

def create_admin_user():
    """管理者ユーザーを作成"""
    # データベース接続
    DATABASE_URL = "sqlite:///./attendance.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("=== 管理者ユーザー作成 ===")
        print()
        
        # 入力を受け取る
        username = input("管理者ユーザー名: ")
        if not username:
            print("ユーザー名は必須です。")
            return
            
        # 既存ユーザーチェック
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            print(f"ユーザー名 '{username}' は既に使用されています。")
            return
        
        email = input("メールアドレス: ")
        if not email:
            print("メールアドレスは必須です。")
            return
            
        # メール重複チェック
        existing_email = db.query(User).filter(User.email == email).first()
        if existing_email:
            print(f"メールアドレス '{email}' は既に使用されています。")
            return
        
        full_name = input("氏名: ")
        if not full_name:
            print("氏名は必須です。")
            return
            
        password = input("パスワード: ")
        if not password:
            print("パスワードは必須です。")
            return
        
        # パスワード確認
        password_confirm = input("パスワード（確認）: ")
        if password != password_confirm:
            print("パスワードが一致しません。")
            return
        
        # 管理者ユーザー作成
        hashed_password = hash_password(password)
        
        admin_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            is_admin=True  # 管理者フラグを設定
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print()
        print("✅ 管理者ユーザーが正常に作成されました！")
        print(f"   ユーザーID: {admin_user.id}")
        print(f"   ユーザー名: {admin_user.username}")
        print(f"   氏名: {admin_user.full_name}")
        print(f"   メール: {admin_user.email}")
        print(f"   管理者権限: はい")
        print()
        print("このユーザーでログインして管理機能を使用できます。")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        db.rollback()
    finally:
        db.close()

def list_users():
    """登録済みユーザー一覧を表示"""
    DATABASE_URL = "sqlite:///./attendance.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        users = db.query(User).all()
        
        if not users:
            print("登録済みユーザーはいません。")
            return
        
        print("=== 登録済みユーザー一覧 ===")
        print()
        print(f"{'ID':<4} {'ユーザー名':<15} {'氏名':<20} {'管理者':<8} {'登録日'}")
        print("-" * 70)
        
        for user in users:
            admin_status = "はい" if user.is_admin else "いいえ"
            created_date = user.created_at.strftime('%Y-%m-%d')
            print(f"{user.id:<4} {user.username:<15} {user.full_name:<20} {admin_status:<8} {created_date}")
        
        print()
        print(f"合計: {len(users)} ユーザー")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
    finally:
        db.close()

def promote_user_to_admin():
    """既存ユーザーを管理者に昇格"""
    DATABASE_URL = "sqlite:///./attendance.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("=== ユーザーを管理者に昇格 ===")
        print()
        
        # ユーザー一覧表示
        users = db.query(User).filter(User.is_admin == False).all()
        if not users:
            print("管理者でないユーザーはいません。")
            return
        
        print("昇格可能なユーザー:")
        for user in users:
            print(f"  {user.id}: {user.username} ({user.full_name})")
        print()
        
        user_id = input("昇格するユーザーのID: ")
        if not user_id.isdigit():
            print("無効なユーザーIDです。")
            return
        
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            print("ユーザーが見つかりません。")
            return
        
        if user.is_admin:
            print("このユーザーは既に管理者です。")
            return
        
        # 確認
        print(f"ユーザー '{user.username}' ({user.full_name}) を管理者に昇格しますか？ (y/N): ", end="")
        confirm = input().lower()
        
        if confirm != 'y' and confirm != 'yes':
            print("昇格をキャンセルしました。")
            return
        
        # 管理者に昇格
        user.is_admin = True
        db.commit()
        
        print()
        print("✅ ユーザーを管理者に昇格しました！")
        print(f"   ユーザー名: {user.username}")
        print(f"   氏名: {user.full_name}")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """メイン関数"""
    print("勤怠管理システム - 管理者ユーザー管理ツール")
    print()
    
    while True:
        print("操作を選択してください:")
        print("1. 管理者ユーザーを新規作成")
        print("2. 登録済みユーザー一覧表示")
        print("3. 既存ユーザーを管理者に昇格")
        print("4. 終了")
        print()
        
        choice = input("選択 (1-4): ")
        print()
        
        if choice == "1":
            create_admin_user()
        elif choice == "2":
            list_users()
        elif choice == "3":
            promote_user_to_admin()
        elif choice == "4":
            print("終了します。")
            break
        else:
            print("無効な選択です。")
        
        print()
        input("何かキーを押して続行...")
        print()

if __name__ == "__main__":
    main()