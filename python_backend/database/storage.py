"""
데이터베이스 스토리지 클래스
사용자 프로필, 변환 기록, 선호도 관리
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from database.models import (
    SessionLocal, UserProfile, ConversionHistory, 
    NegativePreferences
)
