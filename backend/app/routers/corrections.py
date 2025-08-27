"""
修正申請関連のAPIルーター
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..core.database import get_db
from ..core.security import get_current_user, get_current_admin_user
from ..models import User, AttendanceRecord, CorrectionRequest
from ..schemas import CorrectionRequestCreate, CorrectionRequestResponse, CorrectionRequestApproval
from ..services.attendance_utils import time_string_to_datetime, validate_attendance_times, create_log_entry

router = APIRouter(prefix="/correction-request", tags=["修正申請"])

@router.post("/", response_model=dict)
def create_correction_request(
    request: CorrectionRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """修正申請の作成"""
    # 既存の同じ日付の未処理申請をチェック
    existing_request = db.query(CorrectionRequest).filter(
        CorrectionRequest.user_id == current_user.id,
        CorrectionRequest.requested_date == request.requested_date,
        CorrectionRequest.status == "pending"
    ).first()
    
    if existing_request:
        raise HTTPException(
            status_code=400,
            detail="同じ日付で未処理の修正申請が既に存在します"
        )
    
    # 時刻の妥当性チェック（少なくとも出勤か退勤のどちらかは必要）
    try:
        clock_in_dt = time_string_to_datetime(request.requested_date, request.requested_clock_in) if request.requested_clock_in else None
        clock_out_dt = time_string_to_datetime(request.requested_date, request.requested_clock_out) if request.requested_clock_out else None
        break_start_dt = time_string_to_datetime(request.requested_date, request.requested_break_start) if request.requested_break_start else None
        break_end_dt = time_string_to_datetime(request.requested_date, request.requested_break_end) if request.requested_break_end else None
        
        # 少なくとも出勤または退勤のどちらかが設定されている必要がある
        if not clock_in_dt and not clock_out_dt:
            raise HTTPException(status_code=400, detail="出勤時刻または退勤時刻のどちらかは入力してください")
        
        validate_attendance_times(clock_in_dt, clock_out_dt, break_start_dt, break_end_dt)
    except HTTPException:
        raise
    
    # 修正申請の作成
    correction_request = CorrectionRequest(
        user_id=current_user.id,
        attendance_record_id=request.attendance_record_id,
        requested_date=request.requested_date,
        requested_clock_in=clock_in_dt,
        requested_clock_out=clock_out_dt,
        requested_break_start=break_start_dt,
        requested_break_end=break_end_dt,
        requested_notes=request.requested_notes,
        reason=request.reason,
        status="pending"
    )
    
    db.add(correction_request)
    db.commit()
    db.refresh(correction_request)
    
    return {"message": "修正申請を送信しました", "request_id": correction_request.id}

@router.get("/", response_model=List[CorrectionRequestResponse])
def get_correction_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """自分の修正申請一覧取得"""
    requests = db.query(CorrectionRequest).filter(
        CorrectionRequest.user_id == current_user.id
    ).order_by(CorrectionRequest.created_at.desc()).all()
    
    return requests

@router.get("/admin/all", response_model=List[CorrectionRequestResponse])
def get_all_correction_requests(
    status: Optional[str] = None,
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """全修正申請一覧取得（管理者のみ）"""
    query = db.query(CorrectionRequest)
    
    if status:
        query = query.filter(CorrectionRequest.status == status)
    
    requests = query.order_by(CorrectionRequest.created_at.desc()).all()
    return requests

@router.put("/{request_id}/approve")
def approve_correction_request(
    request_id: int,
    approval: CorrectionRequestApproval,
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """修正申請の承認/拒否（管理者のみ）"""
    # 修正申請を取得
    correction_request = db.query(CorrectionRequest).filter(
        CorrectionRequest.id == request_id
    ).first()
    
    if not correction_request:
        raise HTTPException(status_code=404, detail="修正申請が見つかりません")
    
    if correction_request.status != "pending":
        raise HTTPException(status_code=400, detail="既に処理済みの申請です")
    
    # 申請のステータスを更新
    correction_request.status = approval.status
    correction_request.admin_notes = approval.admin_notes
    correction_request.updated_at = datetime.now()
    
    if approval.status == "approved":
        # 承認された場合、実際に勤怠記録を修正
        record = None
        if correction_request.attendance_record_id:
            # 既存記録の修正
            record = db.query(AttendanceRecord).filter(
                AttendanceRecord.id == correction_request.attendance_record_id
            ).first()
        
        if not record:
            # 新規記録の作成
            record = AttendanceRecord(
                user_id=correction_request.user_id,
                date=correction_request.requested_date
            )
            db.add(record)
        
        # 記録を更新
        record.clock_in = correction_request.requested_clock_in
        record.clock_out = correction_request.requested_clock_out
        record.break_start = correction_request.requested_break_start
        record.break_end = correction_request.requested_break_end
        record.notes = correction_request.requested_notes
        
        # ログエントリの作成
        log_entry = create_log_entry("申請承認", admin.username, correction_request.reason, request_id)
        if record.admin_log:
            record.admin_log += "\n" + log_entry
        else:
            record.admin_log = log_entry
    
    db.commit()
    
    status_message = "承認しました" if approval.status == "approved" else "拒否しました"
    return {"message": f"修正申請を{status_message}", "request_id": request_id}