"""변환 API 요청/응답 스키마"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional


class UserProfile(BaseModel):
    """사용자 스타일 프로필 (명시적 스키마)"""
    baseFormalityLevel: int = Field(..., ge=1, le=5, description="격식도 (1-5)")
    baseFriendlinessLevel: int = Field(..., ge=1, le=5, description="친근함 (1-5)")
    baseEmotionLevel: int = Field(..., ge=1, le=5, description="감정표현 (1-5)")
    baseDirectnessLevel: int = Field(..., ge=1, le=5, description="직설성 (1-5)")

    # 세션(일시적) 조정값은 선택적
    sessionFormalityLevel: Optional[int] = Field(None, ge=1, le=5)
    sessionFriendlinessLevel: Optional[int] = Field(None, ge=1, le=5)
    sessionEmotionLevel: Optional[int] = Field(None, ge=1, le=5)
    sessionDirectnessLevel: Optional[int] = Field(None, ge=1, le=5)


class NegativePreferences(BaseModel):
    """네거티브 프롬프트 선호도 (명시적 스키마)"""
    avoidFloweryLanguage: Optional[str] = Field(
        default=None,
        description="과장/수사적 표현 회피 수준 (예: strict/medium/off)"
    )
    avoidSlang: Optional[bool] = Field(default=None, description="속어/은어 회피 여부")
    avoidHonorifics: Optional[bool] = Field(default=None, description="지나친 존칭 회피 여부")
    avoidPassiveAggression: Optional[bool] = Field(default=None, description="수동공격성 표현 회피")

class ConversionRequest(BaseModel):
    """텍스트 변환 요청 모델"""
    text: str = Field(..., min_length=1, max_length=5000, description="변환할 텍스트")
    user_profile: UserProfile = Field(..., description="사용자 프로필")
    context: str = Field(default="personal", description="변환 컨텍스트 (personal, business, report 등)")
    negative_preferences: Optional[NegativePreferences] = Field(default=None, description="네거티브 프롬프트 선호도")

    class Config:
        schema_extra = {
            "example": {
                "text": "회의 자료 검토 부탁드립니다",
                "user_profile": {
                    "baseFormalityLevel": 3,
                    "baseFriendlinessLevel": 4,
                    "baseEmotionLevel": 2,
                    "baseDirectnessLevel": 3
                },
                "context": "business",
                "negative_preferences": {
                    "avoidFloweryLanguage": "strict",
                    "avoidSlang": True
                }
            }
        }

class ConversionResponse(BaseModel):
    """텍스트 변환 응답 모델"""
    success: bool
    original_text: Optional[str] = None
    converted_texts: Optional[Dict[str, str]] = None  # {"direct": "...", "gentle": "...", "neutral": "..."}
    context: Optional[str] = None
    sentiment_analysis: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class FeedbackRequest(BaseModel):
    """피드백 요청 모델"""
    feedback_text: str = Field(..., min_length=1, description="사용자 피드백")
    user_profile: UserProfile = Field(..., description="사용자 프로필")

class FeedbackResponse(BaseModel):
    """피드백 응답 모델"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None