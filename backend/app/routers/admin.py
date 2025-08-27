"""
管理者関連のAPIルーター
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from ..core.database import get_db
from ..core.security import get_current_admin_user
from ..models import User, AttendanceRecord
from ..schemas import AttendanceCorrection, UserResponse
from ..services.attendance_utils import time_string_to_datetime, validate_attendance_times, create_log_entry

router = APIRouter(prefix="/admin", tags=["管理者"])

@router.get("/users", response_model=List[UserResponse])
def get_all_users(db: Session = Depends(get_db), admin: User = Depends(get_current_admin_user)):
    """全ユーザー一覧取得（管理者のみ）"""
    users = db.query(User).all()
    return users

@router.post("/attendance/correct")
def correct_attendance(
    correction: AttendanceCorrection,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    """勤怠記録の直接修正（管理者のみ）"""
    # 対象ユーザーの存在確認
    target_user = db.query(User).filter(User.id == correction.user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="対象ユーザーが見つかりません")
    
    # 該当日の記録を取得または作成
    record = db.query(AttendanceRecord).filter(
        AttendanceRecord.user_id == correction.user_id,
        AttendanceRecord.date == correction.date
    ).first()
    
    if not record:
        record = AttendanceRecord(
            user_id=correction.user_id,
            date=correction.date
        )
        db.add(record)
    
    # 各フィールドを更新
    if correction.clock_in is not None:
        record.clock_in = time_string_to_datetime(correction.date, correction.clock_in)
    if correction.clock_out is not None:
        record.clock_out = time_string_to_datetime(correction.date, correction.clock_out)
    if correction.break_start is not None:
        record.break_start = time_string_to_datetime(correction.date, correction.break_start)
    if correction.break_end is not None:
        record.break_end = time_string_to_datetime(correction.date, correction.break_end)
    if correction.notes is not None:
        record.notes = correction.notes
    
    # 時刻の妥当性チェック
    validate_attendance_times(record.clock_in, record.clock_out, 
                             record.break_start, record.break_end)
    
    # ログエントリの作成
    log_entry = create_log_entry("管理者修正", admin.username, correction.reason)
    if record.admin_log:
        record.admin_log += "\n" + log_entry
    else:
        record.admin_log = log_entry
    
    db.commit()
    db.refresh(record)
    
    return {"message": "勤怠記録を修正しました", "record_id": record.id}