"""
勤怠関連のAPIルーター
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from ..core.database import get_db
from ..models import User, AttendanceRecord
from ..schemas import AttendanceAction, AttendanceResponse
from ..services.attendance_utils import validate_attendance_times

# 依存性注入のための関数（循環インポート回避）
def get_current_user(db: Session = Depends(get_db)) -> User:
    from ..core.security import verify_token, get_db
    from fastapi import Depends
    username = verify_token()
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
    return user

router = APIRouter(prefix="/attendance", tags=["勤怠管理"])

@router.get("/", response_model=List[AttendanceResponse])
def get_attendance_records(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """勤怠記録取得（自分の記録）"""
    query = db.query(AttendanceRecord).filter(AttendanceRecord.user_id == current_user.id)
    
    if start_date:
        query = query.filter(AttendanceRecord.date >= start_date)
    if end_date:
        query = query.filter(AttendanceRecord.date <= end_date)
    
    records = query.order_by(AttendanceRecord.date.desc()).all()
    return records

@router.get("/today", response_model=AttendanceResponse)
def get_today_attendance(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """今日の勤怠状況取得"""
    today = datetime.now().strftime("%Y-%m-%d")
    record = db.query(AttendanceRecord).filter(
        AttendanceRecord.user_id == current_user.id,
        AttendanceRecord.date == today
    ).first()
    
    if not record:
        # 空の記録を返す
        return AttendanceResponse(
            id=0,
            user_id=current_user.id,
            date=today,
            clock_in=None,
            clock_out=None,
            break_start=None,
            break_end=None,
            notes=None,
            status="not_clocked_in"
        )
    
    return record

@router.post("/")
def record_attendance(
    attendance: AttendanceAction, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """勤怠記録（出勤・退勤・休憩開始・終了）"""
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
    
    # 時刻の妥当性チェック
    validate_attendance_times(record.clock_in, record.clock_out, 
                             record.break_start, record.break_end)
    
    db.commit()
    db.refresh(record)
    
    action_messages = {
        'clock_in': '出勤を記録しました',
        'clock_out': '退勤を記録しました', 
        'break_start': '休憩開始を記録しました',
        'break_end': '休憩終了を記録しました'
    }
    
    return {
        "message": action_messages.get(attendance.action, "記録しました"), 
        "record_id": record.id
    }