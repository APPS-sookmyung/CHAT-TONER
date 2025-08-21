"""
Feedback Endpoints
피드백 처리 엔드포인트
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from pydantic import BaseModel

from services.user_preferences import UserPreferencesService
from database.storage import DatabaseStorage

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
    adjustments_made: Dict[str, Any] = {}

# Dependency injection
def get_database_storage():
    return DatabaseStorage()

def get_user_preferences_service(db: DatabaseStorage = Depends(get_database_storage)):
    from services.openai_services import OpenAIService
    openai_service = OpenAIService()
    return UserPreferencesService(db, openai_service)

@router.post("")
async def submit_feedback(
    feedback: FeedbackRequest,
    user_service: UserPreferencesService = Depends(get_user_preferences_service)
) -> FeedbackResponse:
    """사용자 피드백 처리 및 학습"""
    try:
        # 피드백 기반 사용자 선호도 조정
        adjustments = {}
        
        # 선택한 버전과 평점에 따른 선호도 조정 로직
        if feedback.selectedVersion == "direct" and feedback.rating >= 4:
            adjustments["directness_preference"] = "increased"
        elif feedback.selectedVersion == "gentle" and feedback.rating >= 4:
            adjustments["politeness_preference"] = "increased"
        elif feedback.selectedVersion == "neutral" and feedback.rating >= 4:
            adjustments["balance_preference"] = "maintained"
        
        # 낮은 평점의 경우 반대 방향으로 조정
        if feedback.rating <= 2:
            if feedback.selectedVersion == "direct":
                adjustments["directness_preference"] = "decreased"
            elif feedback.selectedVersion == "gentle":
                adjustments["politeness_preference"] = "decreased"
        
        # 실제 학습 로직 (활성화됨)
        user_service.process_feedback(feedback.userId, adjustments)
        
        # 피드백 데이터베이스 저장 (활성화됨)
        was_saved = user_service.save_feedback(feedback)

        if not was_saved:
            raise HTTPException(status_code=400, detail="Failed to save feedback.")
        
        return FeedbackResponse(
            status="success",
            message="피드백이 성공적으로 처리되었습니다. 선호도가 업데이트되었습니다.",
            adjustments_made=adjustments
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"피드백 처리 실패: {str(e)}")

@router.get("/stats/{user_id}")
async def get_feedback_stats(user_id: str) -> Dict[str, Any]:
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