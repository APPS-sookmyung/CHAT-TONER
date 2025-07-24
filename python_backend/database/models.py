"""
SQLAlchemy 모델 정의:
1. User - 기본 사용자 정보
2. UserProfile - 스타일 선호도
3. ConversionHistory - 변환 기록
4. NegativePreferences - 네거티브 프롬프트 설정
"""

import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, JSON, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship