from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional, List
import jwt
import bcrypt
import os

# FastAPIアプリケーション
app = FastAPI(title="勤怠管理システム")

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# データベース設定
DATABASE_URL = "sqlite:///./attendance.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# JWT設定
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# セキュリティ
security = HTTPBearer()

# データベースモデル
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class AttendanceRecord(Base):
    __tablename__ = "attendance_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    date = Column(String, nullable=False)  # YYYY-MM-DD形式
    clock_in = Column(DateTime)
    clock_out = Column(DateTime)
    break_start = Column(DateTime)
    break_end = Column(DateTime)
    notes = Column(Text)
    status = Column(String, default="present")  # present, absent, late, early_leave
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CorrectionRequest(Base):
    __tablename__ = "correction_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    attendance_record_id = Column(Integer)  # 既存記録の修正の場合
    requested_date = Column(String, nullable=False)  # YYYY-MM-DD形式
    requested_clock_in = Column(DateTime)
    requested_clock_out = Column(DateTime)
    requested_break_start = Column(DateTime)
    requested_break_end = Column(DateTime)
    requested_notes = Column(Text)
    reason = Column(Text, nullable=False)  # 申請理由
    status = Column(String, default="pending")  # pending, approved, rejected
    admin_notes = Column(Text)  # 管理者コメント
    approved_by = Column(Integer)  # 承認した管理者のID
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# テーブル作成
Base.metadata.create_all(bind=engine)

# Pydanticモデル（リクエスト/レスポンス）
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: str

class UserLogin(BaseModel):
    username: str
    password: str

class AttendanceCreate(BaseModel):
    action: str  # "clock_in", "clock_out", "break_start", "break_end"
    notes: Optional[str] = None

class AttendanceCorrection(BaseModel):
    user_id: int
    date: str  # YYYY-MM-DD形式
    clock_in: Optional[str] = None  # HH:MM形式
    clock_out: Optional[str] = None
    break_start: Optional[str] = None
    break_end: Optional[str] = None
    notes: Optional[str] = None
    reason: str  # 修正理由

class CorrectionRequestCreate(BaseModel):
    attendance_record_id: Optional[int] = None  # 既存記録の修正の場合
    requested_date: str  # YYYY-MM-DD形式
    requested_clock_in: Optional[str] = None  # HH:MM形式
    requested_clock_out: Optional[str] = None
    requested_break_start: Optional[str] = None
    requested_break_end: Optional[str] = None
    requested_notes: Optional[str] = None
    reason: str  # 申請理由

class CorrectionRequestApproval(BaseModel):
    status: str  # approved, rejected
    admin_notes: Optional[str] = None

class AttendanceResponse(BaseModel):
    id: int
    user_id: int
    date: str
    clock_in: Optional[datetime]
    clock_out: Optional[datetime]
    break_start: Optional[datetime]
    break_end: Optional[datetime]
    notes: Optional[str]
    status: str

# データベースセッション依存性
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# JWT Token関連
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="無効なトークン")
        return username
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="無効なトークン")

def get_current_user(username: str = Depends(verify_token), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
    return user

def get_admin_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="管理者権限が必要です")
    return current_user

# パスワードハッシュ化
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

# API エンドポイント
@app.get("/")
def read_root():
    return {"message": "勤怠管理システムAPI"}

# ユーザー登録
@app.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # ユーザー名とメールの重複チェック
    existing_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="ユーザー名またはメールアドレスが既に使用されています")
    
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

# ログイン
@app.post("/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="ユーザー名またはパスワードが間違っています")
    
    access_token = create_access_token(data={"sub": db_user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": db_user.id,
            "username": db_user.username,
            "full_name": db_user.full_name,
            "is_admin": db_user.is_admin
        }
    }

# 勤怠記録（出勤・退勤・休憩開始・終了）
@app.post("/attendance")
def record_attendance(attendance: AttendanceCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    today = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now()
    
    # 今日の勤怠記録を取得または作成
    record = db.query(AttendanceRecord).filter(
        AttendanceRecord.user_id == current_user.id,
        AttendanceRecord.date == today
    ).first()
    
    if not record:
        record = AttendanceRecord(user_id=current_user.id, date=today)
        db.add(record)
    
    # アクションに応じて記録を更新
    if attendance.action == "clock_in":
        if record.clock_in:
            raise HTTPException(status_code=400, detail="既に出勤記録があります")
        record.clock_in = current_time
        record.status = "present"
    elif attendance.action == "clock_out":
        if not record.clock_in:
            raise HTTPException(status_code=400, detail="出勤記録がありません")
        if record.clock_out:
            raise HTTPException(status_code=400, detail="既に退勤記録があります")
        record.clock_out = current_time
    elif attendance.action == "break_start":
        if not record.clock_in:
            raise HTTPException(status_code=400, detail="出勤記録がありません")
        if record.break_start and not record.break_end:
            raise HTTPException(status_code=400, detail="既に休憩中です")
        record.break_start = current_time
    elif attendance.action == "break_end":
        if not record.break_start:
            raise HTTPException(status_code=400, detail="休憩開始記録がありません")
        if record.break_end:
            raise HTTPException(status_code=400, detail="既に休憩終了記録があります")
        record.break_end = current_time
    else:
        raise HTTPException(status_code=400, detail="無効なアクションです")
    
    if attendance.notes:
        record.notes = attendance.notes
    
    record.updated_at = current_time
    db.commit()
    db.refresh(record)
    
    return {"message": f"{attendance.action}が記録されました", "record_id": record.id}

# 勤怠記録取得（自分の記録）
@app.get("/attendance")
def get_attendance_records(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(AttendanceRecord).filter(AttendanceRecord.user_id == current_user.id)
    
    if start_date:
        query = query.filter(AttendanceRecord.date >= start_date)
    if end_date:
        query = query.filter(AttendanceRecord.date <= end_date)
    
    records = query.order_by(AttendanceRecord.date.desc()).all()
    
    return [
        AttendanceResponse(
            id=record.id,
            user_id=record.user_id,
            date=record.date,
            clock_in=record.clock_in,
            clock_out=record.clock_out,
            break_start=record.break_start,
            break_end=record.break_end,
            notes=record.notes,
            status=record.status
        ) for record in records
    ]

# 今日の勤怠状況取得
@app.get("/attendance/today")
def get_today_attendance(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    today = datetime.now().strftime("%Y-%m-%d")
    record = db.query(AttendanceRecord).filter(
        AttendanceRecord.user_id == current_user.id,
        AttendanceRecord.date == today
    ).first()
    
    if not record:
        return {"date": today, "status": "not_clocked_in"}
    
    return AttendanceResponse(
        id=record.id,
        user_id=record.user_id,
        date=record.date,
        clock_in=record.clock_in,
        clock_out=record.clock_out,
        break_start=record.break_start,
        break_end=record.break_end,
        notes=record.notes,
        status=record.status
    )

# 管理者専用エンドポイント
@app.get("/admin/users")
def get_all_users(admin_user: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [
        {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "email": user.email,
            "is_admin": user.is_admin,
            "created_at": user.created_at
        } for user in users
    ]

@app.get("/admin/attendance/{user_id}")
def get_user_attendance(
    user_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    # ユーザーの存在確認
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
    
    query = db.query(AttendanceRecord).filter(AttendanceRecord.user_id == user_id)
    
    if start_date:
        query = query.filter(AttendanceRecord.date >= start_date)
    if end_date:
        query = query.filter(AttendanceRecord.date <= end_date)
    
    records = query.order_by(AttendanceRecord.date.desc()).all()
    
    return {
        "user": {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name
        },
        "records": [
            AttendanceResponse(
                id=record.id,
                user_id=record.user_id,
                date=record.date,
                clock_in=record.clock_in,
                clock_out=record.clock_out,
                break_start=record.break_start,
                break_end=record.break_end,
                notes=record.notes,
                status=record.status
            ) for record in records
        ]
    }

@app.put("/admin/attendance/{record_id}")
def update_attendance_record(
    record_id: int,
    correction: AttendanceCorrection,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    # 記録の存在確認
    record = db.query(AttendanceRecord).filter(AttendanceRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="勤怠記録が見つかりません")
    
    # 時刻文字列をdatetimeオブジェクトに変換する関数
    def time_string_to_datetime(date_str: str, time_str: str) -> datetime:
        if not time_str:
            return None
        try:
            hour, minute = map(int, time_str.split(':'))
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return date_obj.replace(hour=hour, minute=minute, second=0, microsecond=0)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"無効な時刻形式です: {time_str}")
    
    # 修正データを適用
    if correction.clock_in is not None:
        record.clock_in = time_string_to_datetime(correction.date, correction.clock_in) if correction.clock_in else None
    if correction.clock_out is not None:
        record.clock_out = time_string_to_datetime(correction.date, correction.clock_out) if correction.clock_out else None
    if correction.break_start is not None:
        record.break_start = time_string_to_datetime(correction.date, correction.break_start) if correction.break_start else None
    if correction.break_end is not None:
        record.break_end = time_string_to_datetime(correction.date, correction.break_end) if correction.break_end else None
    if correction.notes is not None:
        record.notes = correction.notes
    
    record.updated_at = datetime.utcnow()
    
    # 修正ログを記録（メモに追記）
    correction_log = f"\n[修正 {datetime.now().strftime('%Y-%m-%d %H:%M')} by {admin_user.username}] {correction.reason}"
    if record.notes:
        record.notes += correction_log
    else:
        record.notes = correction_log
    
    db.commit()
    db.refresh(record)
    
    return {"message": "勤怠記録を修正しました", "record_id": record.id}

@app.post("/admin/attendance/create")
def create_attendance_record(
    correction: AttendanceCorrection,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    # ユーザーの存在確認
    user = db.query(User).filter(User.id == correction.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
    
    # 既存の記録があるかチェック
    existing_record = db.query(AttendanceRecord).filter(
        AttendanceRecord.user_id == correction.user_id,
        AttendanceRecord.date == correction.date
    ).first()
    
    if existing_record:
        raise HTTPException(status_code=400, detail="その日の記録は既に存在します")
    
    # 時刻文字列をdatetimeオブジェクトに変換する関数
    def time_string_to_datetime(date_str: str, time_str: str) -> datetime:
        if not time_str:
            return None
        try:
            hour, minute = map(int, time_str.split(':'))
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return date_obj.replace(hour=hour, minute=minute, second=0, microsecond=0)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"無効な時刻形式です: {time_str}")
    
    # 新しい記録を作成
    new_record = AttendanceRecord(
        user_id=correction.user_id,
        date=correction.date,
        clock_in=time_string_to_datetime(correction.date, correction.clock_in),
        clock_out=time_string_to_datetime(correction.date, correction.clock_out),
        break_start=time_string_to_datetime(correction.date, correction.break_start),
        break_end=time_string_to_datetime(correction.date, correction.break_end),
        status="present"
    )
    
    # 作成ログを記録
    creation_log = f"[作成 {datetime.now().strftime('%Y-%m-%d %H:%M')} by {admin_user.username}] {correction.reason}"
    if correction.notes:
        new_record.notes = f"{correction.notes}\n{creation_log}"
    else:
        new_record.notes = creation_log
    
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    
    return {"message": "勤怠記録を作成しました", "record_id": new_record.id}

# 修正申請関連エンドポイント
@app.post("/correction-request")
def create_correction_request(
    request_data: CorrectionRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    def time_string_to_datetime(date_str: str, time_str: str) -> datetime:
        if not time_str:
            return None
        try:
            hour, minute = map(int, time_str.split(':'))
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return date_obj.replace(hour=hour, minute=minute, second=0, microsecond=0)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"無効な時刻形式です: {time_str}")
    
    # 既存の申請をチェック（同じ日付で承認待ちの申請がないか）
    existing_request = db.query(CorrectionRequest).filter(
        CorrectionRequest.user_id == current_user.id,
        CorrectionRequest.requested_date == request_data.requested_date,
        CorrectionRequest.status == "pending"
    ).first()
    
    if existing_request:
        raise HTTPException(status_code=400, detail="この日付で既に承認待ちの申請があります")
    
    # 新しい修正申請を作成
    correction_request = CorrectionRequest(
        user_id=current_user.id,
        attendance_record_id=request_data.attendance_record_id,
        requested_date=request_data.requested_date,
        requested_clock_in=time_string_to_datetime(request_data.requested_date, request_data.requested_clock_in),
        requested_clock_out=time_string_to_datetime(request_data.requested_date, request_data.requested_clock_out),
        requested_break_start=time_string_to_datetime(request_data.requested_date, request_data.requested_break_start),
        requested_break_end=time_string_to_datetime(request_data.requested_date, request_data.requested_break_end),
        requested_notes=request_data.requested_notes,
        reason=request_data.reason
    )
    
    db.add(correction_request)
    db.commit()
    db.refresh(correction_request)
    
    return {"message": "修正申請を送信しました", "request_id": correction_request.id}

@app.get("/correction-requests")
def get_my_correction_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    requests = db.query(CorrectionRequest).filter(
        CorrectionRequest.user_id == current_user.id
    ).order_by(CorrectionRequest.created_at.desc()).all()
    
    return [
        {
            "id": req.id,
            "attendance_record_id": req.attendance_record_id,
            "requested_date": req.requested_date,
            "requested_clock_in": req.requested_clock_in,
            "requested_clock_out": req.requested_clock_out,
            "requested_break_start": req.requested_break_start,
            "requested_break_end": req.requested_break_end,
            "requested_notes": req.requested_notes,
            "reason": req.reason,
            "status": req.status,
            "admin_notes": req.admin_notes,
            "created_at": req.created_at,
            "updated_at": req.updated_at
        } for req in requests
    ]

@app.get("/admin/correction-requests")
def get_all_correction_requests(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    requests = db.query(CorrectionRequest).order_by(
        CorrectionRequest.status.asc(),  # pending を最初に
        CorrectionRequest.created_at.desc()
    ).all()
    
    result = []
    for req in requests:
        user = db.query(User).filter(User.id == req.user_id).first()
        result.append({
            "id": req.id,
            "user": {
                "id": user.id,
                "username": user.username,
                "full_name": user.full_name
            },
            "attendance_record_id": req.attendance_record_id,
            "requested_date": req.requested_date,
            "requested_clock_in": req.requested_clock_in,
            "requested_clock_out": req.requested_clock_out,
            "requested_break_start": req.requested_break_start,
            "requested_break_end": req.requested_break_end,
            "requested_notes": req.requested_notes,
            "reason": req.reason,
            "status": req.status,
            "admin_notes": req.admin_notes,
            "created_at": req.created_at,
            "updated_at": req.updated_at
        })
    
    return result

@app.put("/admin/correction-requests/{request_id}")
def process_correction_request(
    request_id: int,
    approval: CorrectionRequestApproval,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    # 申請を取得
    correction_request = db.query(CorrectionRequest).filter(
        CorrectionRequest.id == request_id
    ).first()
    
    if not correction_request:
        raise HTTPException(status_code=404, detail="修正申請が見つかりません")
    
    if correction_request.status != "pending":
        raise HTTPException(status_code=400, detail="この申請は既に処理済みです")
    
    # 申請のステータスを更新
    correction_request.status = approval.status
    correction_request.admin_notes = approval.admin_notes
    correction_request.approved_by = admin_user.id
    correction_request.updated_at = datetime.utcnow()
    
    # 承認の場合、実際の勤怠記録を更新または作成
    if approval.status == "approved":
        if correction_request.attendance_record_id:
            # 既存記録の修正
            record = db.query(AttendanceRecord).filter(
                AttendanceRecord.id == correction_request.attendance_record_id
            ).first()
            if record:
                record.clock_in = correction_request.requested_clock_in
                record.clock_out = correction_request.requested_clock_out
                record.break_start = correction_request.requested_break_start
                record.break_end = correction_request.requested_break_end
                record.notes = correction_request.requested_notes
                record.updated_at = datetime.utcnow()
                
                # 修正ログを追加
                log_entry = f"\n[修正承認 {datetime.now().strftime('%Y-%m-%d %H:%M')} by {admin_user.username}] 申請ID: {request_id}"
                if record.notes:
                    record.notes += log_entry
                else:
                    record.notes = log_entry
        else:
            # 新規記録の作成
            new_record = AttendanceRecord(
                user_id=correction_request.user_id,
                date=correction_request.requested_date,
                clock_in=correction_request.requested_clock_in,
                clock_out=correction_request.requested_clock_out,
                break_start=correction_request.requested_break_start,
                break_end=correction_request.requested_break_end,
                notes=correction_request.requested_notes,
                status="present"
            )
            
            # 作成ログを追加
            creation_log = f"[申請承認作成 {datetime.now().strftime('%Y-%m-%d %H:%M')} by {admin_user.username}] 申請ID: {request_id}"
            if new_record.notes:
                new_record.notes = f"{new_record.notes}\n{creation_log}"
            else:
                new_record.notes = creation_log
            
            db.add(new_record)
    
    db.commit()
    
    status_text = "承認" if approval.status == "approved" else "却下"
    return {"message": f"修正申請を{status_text}しました"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)