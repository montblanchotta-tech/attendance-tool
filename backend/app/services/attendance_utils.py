"""
勤怠関連のユーティリティ関数
"""
from datetime import datetime
from typing import Optional
from fastapi import HTTPException

def time_string_to_datetime(date_str: str, time_str: Optional[str]) -> Optional[datetime]:
    """時刻文字列をdatetimeオブジェクトに変換"""
    if not time_str:
        return None
    try:
        hour, minute = map(int, time_str.split(':'))
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.replace(hour=hour, minute=minute, second=0, microsecond=0)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"無効な時刻形式です: {time_str}")

def validate_attendance_times(clock_in: Optional[datetime], 
                             clock_out: Optional[datetime],
                             break_start: Optional[datetime], 
                             break_end: Optional[datetime]) -> None:
    """勤怠時刻の妥当性をチェック"""
    if clock_in and clock_out and clock_in >= clock_out:
        raise HTTPException(status_code=400, detail="退勤時刻は出勤時刻より後である必要があります")
    
    if break_start and break_end and break_start >= break_end:
        raise HTTPException(status_code=400, detail="休憩終了時刻は休憩開始時刻より後である必要があります")
    
    if break_start and clock_in and break_start <= clock_in:
        raise HTTPException(status_code=400, detail="休憩開始時刻は出勤時刻より後である必要があります")
    
    if break_end and clock_out and break_end >= clock_out:
        raise HTTPException(status_code=400, detail="休憩終了時刻は退勤時刻より前である必要があります")

def create_log_entry(action: str, admin_username: str, reason: str, request_id: Optional[int] = None) -> str:
    """操作ログエントリを作成"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    base_log = f"[{action} {timestamp} by {admin_username}]"
    
    if request_id:
        base_log += f" 申請ID: {request_id}"
    
    if reason:
        base_log += f" {reason}"
    
    return base_log