"""
レポート関連のAPIルーター
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from ..core.database import get_db
from ..core.security import get_current_admin_user
from ..models import User, AttendanceRecord

router = APIRouter(prefix="/reports", tags=["レポート"])

@router.get("/attendance-summary")
def get_attendance_summary(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    user_id: Optional[int] = None,
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """勤怠サマリーレポート（管理者のみ）"""
    query = db.query(AttendanceRecord)
    
    if start_date:
        query = query.filter(AttendanceRecord.date >= start_date)
    if end_date:
        query = query.filter(AttendanceRecord.date <= end_date)
    if user_id:
        query = query.filter(AttendanceRecord.user_id == user_id)
    
    records = query.all()
    
    summary = []
    for record in records:
        work_hours = 0
        break_hours = 0
        
        if record.clock_in and record.clock_out:
            total_time = record.clock_out - record.clock_in
            work_hours = total_time.total_seconds() / 3600
            
            if record.break_start and record.break_end:
                break_time = record.break_end - record.break_start
                break_hours = break_time.total_seconds() / 3600
                work_hours -= break_hours
        
        summary.append({
            "user_id": record.user_id,
            "date": record.date,
            "clock_in": record.clock_in,
            "clock_out": record.clock_out,
            "break_start": record.break_start,
            "break_end": record.break_end,
            "work_hours": round(work_hours, 2),
            "break_hours": round(break_hours, 2),
            "status": record.status,
            "notes": record.notes
        })
    
    return {"summary": summary, "total_records": len(summary)}