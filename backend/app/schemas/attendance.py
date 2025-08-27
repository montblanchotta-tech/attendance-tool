"""
勤怠関連のPydanticスキーマ
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AttendanceAction(BaseModel):
    action: str  # "clock_in", "clock_out", "break_start", "break_end"
    notes: Optional[str] = None

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
    
    class Config:
        from_attributes = True

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

class CorrectionRequestResponse(BaseModel):
    id: int
    attendance_record_id: Optional[int]
    requested_date: str
    requested_clock_in: Optional[datetime]
    requested_clock_out: Optional[datetime]
    requested_break_start: Optional[datetime]
    requested_break_end: Optional[datetime]
    requested_notes: Optional[str]
    reason: str
    status: str
    admin_notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class CorrectionRequestApproval(BaseModel):
    status: str  # approved, rejected
    admin_notes: Optional[str] = None