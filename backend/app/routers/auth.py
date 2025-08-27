"""
認証関連のAPIルーター
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..core.security import hash_password, verify_password, create_access_token
from ..models import User
from ..schemas import UserCreate, UserLogin, Token, UserResponse

router = APIRouter(prefix="/auth", tags=["認証"])

@router.post("/register", response_model=dict)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """新規ユーザー登録"""
    # ユーザー名とメールの重複チェック
    existing_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=400, 
            detail="ユーザー名またはメールアドレスが既に使用されています"
        )
    
    # パスワードハッシュ化
    hashed_password = hash_password(user.password)
    
    # 新規ユーザー作成
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {"message": "ユーザー登録が完了しました", "user_id": db_user.id}

@router.post("/login", response_model=Token)
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    """ユーザーログイン"""
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=401, 
            detail="ユーザー名またはパスワードが間違っています"
        )
    
    access_token = create_access_token(data={"sub": db_user.username})
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            full_name=db_user.full_name,
            is_admin=db_user.is_admin,
            created_at=db_user.created_at
        )
    )