"""
Feedback Endpoints
피드백 처리 엔드포인트
get_feedback_stats 함수에 누락된 user_service 의존성 주입 파라미터 추가
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from pydantic import BaseModel

from services.user_preferences import UserPreferencesService
from database.storage import DatabaseStorage
from typing import List

router = APIRouter()

# Request/Response Models
class FeedbackRequest(BaseModel):
    conversionId: int
    selectedVersion: str  # direct, gentle, neutral
    rating: int  # 1-5 점수
    userId: str = "default"
    feedback_text: str = ""

class FeedbackResponse(BaseModel):
    status: str
    message: str
    feedbackId: int
    timestamp: str

# Dependency injection
def get_database_storage():
    return DatabaseStorage()

def get_user_preferences_service(db: DatabaseStorage = Depends(get_database_storage)):
    from services.openai_services import OpenAIService
    openai_service = OpenAIService()
    return UserPreferencesService(db, openai_service)

@router.post("", response_model=FeedbackResponse)
async def submit_feedback(
    feedback: FeedbackRequest,
    user_service: UserPreferencesService = Depends(get_user_preferences_service)
) -> FeedbackResponse:
    """사용자 피드백 처리 및 학습"""
    try:
        # 서비스 레이어를 호출하여 피드백을 저장하고 업데이트된 기록을 받음
        updated_record = user_service.save_feedback(feedback)

        if not updated_record:
            raise HTTPException(status_code=400, detail="피드백 저장에 실패했습니다. 해당 ID의 변환 기록을 찾을 수 없습니다.")
        
        return FeedbackResponse(
            status="success",
            message="피드백이 성공적으로 처리 및 저장되었습니다.",
            feedbackId=updated_record['id'],
            timestamp=updated_record['updated_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"피드백 처리 실패: {str(e)}")

@router.get("/stats/{user_id}")
async def get_feedback_stats(
    user_id: str,
    user_service: UserPreferencesService = Depends(get_user_preferences_service)
) -> Dict[str, Any]:
    """사용자의 피드백 통계 조회"""
    try:
        # 실제 통계 조회 (활성화됨)
        stats = user_service.get_feedback_stats(user_id)
        
        if stats is not None:
            return stats

        raise HTTPException(status_code=404, detail=f"Statistics for user '{user_id}' not found.")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"통계 조회 실패: {str(e)}")
    
class NegativePromptUpdate(BaseModel):
    """네거티브 프롬프트 수정을 위한 Pydantic 모델"""
    negative_prompts: List[str] = []

class UserProfileResponse(BaseModel):
    """사용자 프로필 조회 응답을 위한 Pydantic 모델"""
    user_id: str
    negative_prompts: List[str]
    # 다른 프로필 정보 추가 가능

    class Config:
        from_attributes = True # DB 모델 객체를 Pydantic 모델로 변환 가능