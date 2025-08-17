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

@router.get("/{user_id}", response_model=ProfileResponse, summary="사용자 프로필 조회", description="사용자의 개인화 설정을 조회합니다.")
async def get_user_profile(
    user_id: str,
    user_service: UserPreferencesService = Depends(get_user_preferences_service)
) -> ProfileResponse:
    """
    ## 사용자 프로필 조회

    사용자의 텍스트 스타일 개인화 설정을 반환합니다.
    """
    try:
        profile_data = user_service.get_user_profile(user_id)

        if not profile_data:
            raise HTTPException(status_code=404, detail=f"Profile for user '{user_id}' not found.")

        # 데이터베이스 응답을 API 응답 모델(ProfileResponse)에 맞게 매핑합니다.
        return ProfileResponse(
            id=profile_data.get("id", 1),  # 'id'가 없으므로 임시 ID 사용
            userId=profile_data.get("userId"),
            baseFormalityLevel=profile_data.get("baseFormalityLevel"),
            baseFriendlinessLevel=profile_data.get("baseFriendlinessLevel"),
            baseEmotionLevel=profile_data.get("baseEmotionLevel"),
            baseDirectnessLevel=profile_data.get("baseDirectnessLevel"),
            # 세션 값이 없으면 기본값을 사용합니다.
            sessionFormalityLevel=profile_data.get("sessionFormalityLevel") or profile_data.get("baseFormalityLevel"),
            sessionFriendlinessLevel=profile_data.get("sessionFriendlinessLevel") or profile_data.get("baseFriendlinessLevel"),
            sessionEmotionLevel=profile_data.get("sessionEmotionLevel") or profile_data.get("baseEmotionLevel"),
            sessionDirectnessLevel=profile_data.get("sessionDirectnessLevel") or profile_data.get("baseDirectnessLevel"),
            responses=profile_data.get("questionnaireResponses", {}),
            completedAt=profile_data.get("updatedAt") or profile_data.get("createdAt")
        )
    except HTTPException:
        raise
    except Exception as e:
        # Pydantic validation error 등 다른 예외 처리
        raise HTTPException(status_code=500, detail=f"프로필 조회 실패: {str(e)}")

@router.post("", response_model=ProfileResponse, summary="사용자 프로필 저장", description="사용자의 개인화 설정을 저장합니다.")
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
        # 실제 서비스에서 프로필 저장 (활성화됨)
        # 참고: user_service.save_user_profile의 인자나 반환 값에 따라 수정이 필요할 수 있습니다.
        was_saved = user_service.save_user_profile(profile.userId, profile.model_dump())

        if not was_saved:
            raise HTTPException(status_code=400, detail="Failed to save profile.")

        # 저장 성공 후, 저장된 프로필 정보를 다시 조회하여 반환하는 것이 가장 이상적입니다.
        # 여기서는 요청된 데이터를 기반으로 응답을 생성합니다.
        return ProfileResponse(
            id=1, # 임시 ID
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
            completedAt="2025-08-10T00:00:00Z" # 저장 시간으로 변경 필요
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"프로필 저장 실패: {str(e)}")