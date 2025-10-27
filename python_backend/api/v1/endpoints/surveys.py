from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
import logging

# Temporarily disable these imports to avoid dependency issues
# from services.profile_pipeline import run_profile_pipeline
# from services.vector_store_pg import VectorStorePG
# from api.dependencies import get_vector_store

logger = logging.getLogger('chattoner.surveys')


router = APIRouter(tags=["surveys"])


class SurveySchema(BaseModel):
    title: str
    questions: List[Dict[str, Any]]


@router.get("/{key}", response_model=SurveySchema)
async def get_survey(key: str):
    if key != "onboarding-intake":
        raise HTTPException(404, "unknown survey key")
    return SurveySchema(
        title="온보딩 인테이크",
        questions=[
            {"id": "primary_function", "type": "single_select", "label": {"ko": "주 업무 범주"}, "options": ["engineering", "sales", "operations", "hr", "finance"], "required": True},
            {"id": "communication_style", "type": "single_select", "label": {"ko": "소통 성격"}, "options": ["friendly", "formal", "strict", "casual"], "required": True},
            {"id": "team_size", "type": "single_select", "label": {"ko": "인원 수"}, "options": ["1-10", "11-50", "51-200", "201-1000", "1001+"], "required": True},
            {"id": "primary_channel", "type": "single_select", "label": {"ko": "주된 커뮤니케이션 채널"}, "options": ["email", "chat", "report", "meeting_minutes"], "required": True},
            {"id": "primary_audience", "type": "multi_select", "label": {"ko": "주 커뮤니케이션 대상"}, "options": ["peers_internal", "cross_team", "executives", "clients_vendors"], "required": True},
        ],
    )


class SubmitRequest(BaseModel):
    tenant_id: str
    user_id: str
    answers: Dict[str, Any]


@router.post("/{key}/responses")
async def submit_survey(key: str, req: SubmitRequest):
    if key != "onboarding-intake":
        raise HTTPException(404, "unknown survey key")
    try:
        # Temporarily return mock data
        return {
            "id": 1,
            "userId": req.user_id,
            "baseFormalityLevel": 75,
            "baseFriendlinessLevel": 60,
            "baseEmotionLevel": 50,
            "baseDirectnessLevel": 80,
            "sessionFormalityLevel": 75,
            "sessionFriendlinessLevel": 60,
            "sessionEmotionLevel": 50,
            "sessionDirectnessLevel": 80,
            "responses": req.answers,
            "completedAt": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        logger.error(f"설문 처리 중 오류 발생: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred during survey processing.")

