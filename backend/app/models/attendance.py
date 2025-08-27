"""
勤怠記録モデル
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base

class AttendanceRecord(Base):
    __tablename__ = "attendance_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(String, nullable=False)  # YYYY-MM-DD形式
    clock_in = Column(DateTime)
    clock_out = Column(DateTime)
    break_start = Column(DateTime)
    break_end = Column(DateTime)
    notes = Column(Text)
    status = Column(String, default="present")  # present, absent, late, early_leave
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<AttendanceRecord(id={self.id}, user_id={self.user_id}, date='{self.date}')>"

class CorrectionRequest(Base):
    __tablename__ = "correction_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    attendance_record_id = Column(Integer, ForeignKey("attendance_records.id"))  # 既存記録の修正の場合
    requested_date = Column(String, nullable=False)  # YYYY-MM-DD形式
    requested_clock_in = Column(DateTime)
    requested_clock_out = Column(DateTime)
    requested_break_start = Column(DateTime)
    requested_break_end = Column(DateTime)
    requested_notes = Column(Text)
    reason = Column(Text, nullable=False)  # 申請理由
    status = Column(String, default="pending")  # pending, approved, rejected
    admin_notes = Column(Text)  # 管理者コメント
    approved_by = Column(Integer, ForeignKey("users.id"))  # 承認した管理者のID
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<CorrectionRequest(id={self.id}, user_id={self.user_id}, status='{self.status}')>"