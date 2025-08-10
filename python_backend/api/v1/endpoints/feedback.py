"""
Feedback Endpoints
피드백 처리 엔드포인트
"""

from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends
from dependency_injector.wiring import inject, Provide

from core.container import Container
from services.conversion_service import ConversionService
from api.v1.schemas.conversion import (
    FeedbackRequest,
    FeedbackResponse
)
import logging

logger = logging.getLogger('chattoner')

router = APIRouter()

@router.post("/feedback", response_model=FeedbackResponse)
@inject
async def process_feedback(
    request: FeedbackRequest,
    conversion_service: Annotated[
        ConversionService, 
        Depends(Provide[Container.conversion_service])
    ]
) -> FeedbackResponse:
    """사용자 피드백 처리"""
    try:
        result = await conversion_service.process_user_feedback(
            feedback_text=request.feedback_text,
            user_profile=request.user_profile
        )
        return FeedbackResponse(success=True, message="피드백이 반영되었습니다.", data=result)
    
    except Exception as e:
        logger.error(f"피드백 처리 실패: {e}")
        raise HTTPException(status_code=500, detail="피드백 처리 중 오류가 발생했습니다.") from e