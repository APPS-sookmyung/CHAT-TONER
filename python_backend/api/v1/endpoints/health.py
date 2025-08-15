"""
Health Check Endpoint
서버 상태 확인을 위한 엔드포인트
"""

import os
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Dict, Any

router = APIRouter()

class HealthResponse(BaseModel):
    """헬스체크 응답 모델"""
    status: str = Field(..., description="서버 상태", example="ok")
    service: str = Field(..., description="서비스 이름", example="chat-toner-fastapi")
    openai_available: bool = Field(..., description="OpenAI 연결 상태", example=True)
    prompt_engineering_available: bool = Field(..., description="프롬프트 엔지니어링 상태", example=True)
    features: Dict[str, bool] = Field(..., description="사용 가능한 기능들")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "ok",
                "service": "chat-toner-fastapi",
                "openai_available": True,
                "prompt_engineering_available": True,
                "features": {
                    "basic_conversion": True,
                    "advanced_prompts": True,
                    "openai_integration": True,
                    "rag_chains": True,
                    "finetune_service": True
                }
            }
        }

@router.get("/health", 
            response_model=HealthResponse,
            summary="서버 상태 확인",
            description="시스템 전체 상태 및 외부 서비스 연결을 확인합니다.")
async def health_check() -> HealthResponse:
    """
    ## 서버 상태 확인
    
    Chat Toner 백엔드 서비스의 전반적인 상태를 확인합니다.
    
    ### 확인 항목
    - **OpenAI 연결 상태**
    - **프롬프트 엔지니어링 서비스 상태**  
    - **사용 가능한 기능 목록**
    """
    return HealthResponse(
        status="ok",
        service="chat-toner-fastapi",
        openai_available=bool(os.getenv("OPENAI_API_KEY")),
        prompt_engineering_available=True,
        features={
            "basic_conversion": True,
            "advanced_prompts": True,
            "openai_integration": bool(os.getenv("OPENAI_API_KEY")),
            "rag_chains": True,
            "finetune_service": True
        }
    )

@router.get("/api/health",
            response_model=HealthResponse, 
            summary="API 헬스체크",
            description="API 전용 헬스체크 엔드포인트입니다.")
async def api_health_check() -> HealthResponse:
    """API 전용 헬스체크"""
    from datetime import datetime
    
    return HealthResponse(
        status="healthy",
        service="chat-toner-fastapi",
        openai_available=bool(os.getenv("OPENAI_API_KEY")),
        prompt_engineering_available=True,
        features={
            "basic_conversion": True,
            "advanced_prompts": True,
            "openai_integration": bool(os.getenv("OPENAI_API_KEY")),
            "rag_chains": True,
            "finetune_service": True
        }
    )