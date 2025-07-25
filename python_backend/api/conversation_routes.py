"""
텍스트 변환 API 라우트
- 이 API는 텍스트 스타일 변환을 위한 엔드포인트를 제공합
- 즉 FastAPI 기반의 라우터 파일로, 외부에서 요청을 받을 실제 API endpoint를 정의
- 사용자 피드백을 처리하는 엔드포인트도 포함
- 변환 요청과 피드백 요청을 처리하는 메소드 포함

"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from ..services.conversion_service import ConversionService

router = APIRouter(prefix="/api/conversion", tags=["conversion"])

class ConversionRequest(BaseModel):
    text: str
    user_profile: Dict[str, Any]
    context: str = "personal"
    negative_preferences: Optional[Dict[str, str]] = None

class FeedbackRequest(BaseModel):
    feedback_text: str
    user_profile: Dict[str, Any]

# 서비스 인스턴스
conversion_service = ConversionService()

@router.post("/convert")
async def convert_text(request: ConversionRequest):
    """텍스트 스타일 변환"""
    try:
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="변환할 텍스트를 입력해주세요.")
        
        if len(request.text) > 5000:
            raise HTTPException(status_code=400, detail="텍스트가 너무 깁니다. 5000자 이하로 입력해주세요.")
        
        result = await conversion_service.convert_text(
            input_text=request.text,
            user_profile=request.user_profile,
            context=request.context,
            negative_preferences=request.negative_preferences
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "변환 중 오류가 발생했습니다."))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

@router.post("/feedback")
async def process_feedback(request: FeedbackRequest):
    """사용자 피드백 처리"""
    try:
        if not request.feedback_text.strip():
            raise HTTPException(status_code=400, detail="피드백을 입력해주세요.")
        
        result = await conversion_service.process_user_feedback(
            feedback_text=request.feedback_text,
            user_profile=request.user_profile
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "피드백 처리 중 오류가 발생했습니다."))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

@router.get("/health")
async def health_check():
    """서비스 상태 확인"""
    return {
        "status": "healthy",
        "service": "conversion_service",
        "timestamp": conversion_service._get_timestamp()
    }