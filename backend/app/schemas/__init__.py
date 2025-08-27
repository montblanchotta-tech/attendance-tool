"""
スキーマ統合ファイル
"""
from .user import UserCreate, UserResponse, UserLogin, Token
from .attendance import (
    AttendanceAction,
    AttendanceResponse,
    AttendanceCorrection,
    CorrectionRequestCreate,
    CorrectionRequestResponse,
    CorrectionRequestApproval
)

__all__ = [
    "UserCreate",
    "UserResponse", 
    "UserLogin",
    "Token",
    "AttendanceAction",
    "AttendanceResponse",
    "AttendanceCorrection",
    "CorrectionRequestCreate",
    "CorrectionRequestResponse",
    "CorrectionRequestApproval"
]