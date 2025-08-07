"""변환 API 요청/응답 스키마"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List

class ConversionRequest(BaseModel):
    """텍스트 변환 요청 모델"""
    text: str = Field(..., min_length=1, max_length=5000, description="변환할 텍스트")
    user_profile: Dict[str, Any] = Field(..., description="사용자 프로필")
    context: str = Field(default="personal", description="변환 컨텍스트 (personal, business, report 등)")
    negative_preferences: Optional[Dict[str, str]] = Field(default=None, description="네거티브 프롬프트 선호도")

    class Config:
        schema_extra = {
            "example": {
                "text": "안녕하세요! 비즈니스 이메일 작성을 도와주세요.",
                "user_profile": {"formality_level": 4},
                "context": "business",
                "negative_preferences": {"avoid_flowery_language": "strict"}
            }
        }

class ConversionResponse(BaseModel):
    """텍스트 변환 응답 모델"""
    success: bool
    converted_text: Optional[str] = None
    variations: Optional[Dict[str, str]] = None
    sentiment_analysis: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class FeedbackRequest(BaseModel):
    """피드백 요청 모델"""
    feedback_text: str = Field(..., min_length=1, description="사용자 피드백")
    user_profile: Dict[str, Any] = Field(..., description="사용자 프로필")

class FeedbackResponse(BaseModel):
    """피드백 응답 모델"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None