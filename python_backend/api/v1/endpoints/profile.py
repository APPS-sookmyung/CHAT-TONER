"""
User Profile Endpoints
사용자 프로필 관리 엔드포인트
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from services.user_preferences import UserPreferencesService
from database.storage import DatabaseStorage

router = APIRouter()

# Request/Response Models
class ProfileRequest(BaseModel):
    userId: str
    baseFormalityLevel: int = Field(default=5, ge=1, le=5, description="격식도 수준 (1-5)", example=5)
    baseFriendlinessLevel: int = Field(default=5, ge=1, le=5, description="친근함 수준 (1-5)", example=5)
    baseEmotionLevel: int = Field(default=5, ge=1, le=5, description="감정 표현 수준 (1-5)", example=5)
    baseDirectnessLevel: int = Field(default=5, ge=1, le=5, description="직설성 수준 (1-5)", example=5)
    sessionFormalityLevel: Optional[int] = Field(None, ge=1, le=5, description="세션별 격식도 수준")
    sessionFriendlinessLevel: Optional[int] = Field(None, ge=1, le=5, description="세션별 친근함 수준")
    sessionEmotionLevel: Optional[int] = Field(None, ge=1, le=5, description="세션별 감정 표현 수준")
    sessionDirectnessLevel: Optional[int] = Field(None, ge=1, le=5, description="세션별 직설성 수준")
    responses: Optional[Dict[str, Any]] = Field(default_factory=dict, description="추가 응답 데이터")

    class Config:
        schema_extra = {
            "example": {
                "userId": "user456",
                "baseFormalityLevel": 4,
                "baseFriendlinessLevel": 3,
                "baseEmotionLevel": 5,
                "baseDirectnessLevel": 2,
                "sessionFormalityLevel": 3,
                "sessionFriendlinessLevel": 4,
                "sessionEmotionLevel": 5,
                "sessionDirectnessLevel": 3,
                "responses": {"greeting": "Hello!"}
            }
        }

class ProfileResponse(BaseModel):
    id: int
    userId: str
    baseFormalityLevel: int
    baseFriendlinessLevel: int
    baseEmotionLevel: int
    baseDirectnessLevel: int
    sessionFormalityLevel: int
    sessionFriendlinessLevel: int
    sessionEmotionLevel: int
    sessionDirectnessLevel: int
    responses: Dict[str, Any]
    completedAt: str

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "userId": "user456",
                "baseFormalityLevel": 4,
                "baseFriendlinessLevel": 3,
                "baseEmotionLevel": 5,
                "baseDirectnessLevel": 2,
                "sessionFormalityLevel": 3,
                "sessionFriendlinessLevel": 4,
                "sessionEmotionLevel": 5,
                "sessionDirectnessLevel": 3,
                "responses": {"greeting": "Hello!"},
                "completedAt": "2025-08-10T00:00:00Z"
            }
        }

# Dependency injection
def get_database_storage():
    return DatabaseStorage()

def get_user_preferences_service(db: DatabaseStorage = Depends(get_database_storage)):
    from services.openai_services import OpenAIService
    openai_service = OpenAIService()
    return UserPreferencesService(db, openai_service)

@router.get("/profile/{user_id}", response_model=ProfileResponse, summary="사용자 프로필 조회", description="사용자의 개인화 설정을 조회합니다.")
async def get_user_profile(
    user_id: str,
    user_service: UserPreferencesService = Depends(get_user_preferences_service)
) -> ProfileResponse:
    """
    ## 사용자 프로필 조회

    사용자의 텍스트 스타일 개인화 설정을 반환합니다.

    ### 경로 매개변수
    - `user_id`: 조회할 사용자의 고유 ID

    ### 응답 항목
    - `userId`: 사용자 ID
    - `baseFormalityLevel`: 기본 격식도 수준 (1: 매우 캐주얼, 5: 매우 격식)
    - `baseFriendlinessLevel`: 기본 친근함 수준 (1: 거리감, 5: 매우 친근)
    - `baseEmotionLevel`: 기본 감정 표현 수준 (1: 담담함, 5: 감정적)
    - `baseDirectnessLevel`: 기본 직설성 수준 (1: 돌려 말함, 5: 직설적)
    - `sessionFormalityLevel`: 현재 세션의 격식도 수준 (설정되지 않은 경우 기본값 사용)
    - `sessionFriendlinessLevel`: 현재 세션의 친근함 수준 (설정되지 않은 경우 기본값 사용)
    - `sessionEmotionLevel`: 현재 세션의 감정 표현 수준 (설정되지 않은 경우 기본값 사용)
    - `sessionDirectnessLevel`: 현재 세션의 직설성 수준 (설정되지 않은 경우 기본값 사용)
    - `responses`: 저장된 추가 응답 데이터
    - `completedAt`: 프로필 정보가 마지막으로 업데이트된 시간
    """
    try:
        # 실제 서비스에서 프로필 조회 (향후 구현)
        # profile = await user_service.get_user_profile(user_id)

        # 현재는 기본 프로필 반환
        return ProfileResponse(
            id=1,
            userId=user_id,
            baseFormalityLevel=5,
            baseFriendlinessLevel=5,
            baseEmotionLevel=5,
            baseDirectnessLevel=5,
            sessionFormalityLevel=5,
            sessionFriendlinessLevel=5,
            sessionEmotionLevel=5,
            sessionDirectnessLevel=5,
            responses={},
            completedAt="2025-08-10T00:00:00Z"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"프로필 조회 실패: {str(e)}")

@router.post("/profile", response_model=ProfileResponse, summary="사용자 프로필 저장", description="사용자의 개인화 설정을 저장합니다.")
async def save_user_profile(
    profile: ProfileRequest,
    user_service: UserPreferencesService = Depends(get_user_preferences_service)
) -> ProfileResponse:
    """
    ## 사용자 프로필 저장

    새로운 사용자 프로필 설정을 저장하거나 기존 설정을 업데이트합니다.

    ### 요청 본문
    - `profile`: 저장할 사용자 프로필 데이터
    """
    try:
        # 실제 서비스에서 프로필 저장 (향후 구현)
        # saved_profile = await user_service.save_user_profile(profile)

        # 현재는 요청 데이터로 응답 생성
        return ProfileResponse(
            id=1,
            userId=profile.userId,
            baseFormalityLevel=profile.baseFormalityLevel,
            baseFriendlinessLevel=profile.baseFriendlinessLevel,
            baseEmotionLevel=profile.baseEmotionLevel,
            baseDirectnessLevel=profile.baseDirectnessLevel,
            sessionFormalityLevel=profile.sessionFormalityLevel or profile.baseFormalityLevel,
            sessionFriendlinessLevel=profile.sessionFriendlinessLevel or profile.baseFriendlinessLevel,
            sessionEmotionLevel=profile.sessionEmotionLevel or profile.baseEmotionLevel,
            sessionDirectnessLevel=profile.sessionDirectnessLevel or profile.baseDirectnessLevel,
            responses=profile.responses or {},
            completedAt="2025-08-10T00:00:00Z"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"프로필 저장 실패: {str(e)}")