"""
Health Check Endpoint
서버 상태 확인을 위한 엔드포인트
"""

import os
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from core.config import get_settings
from sqlalchemy import inspect #헬스체크 추가 api 
from database.db import engine

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
                    "rag_chains": True
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
    settings = get_settings()
    return HealthResponse(
        status="ok",
        service="chat-toner-fastapi",
        openai_available=bool(settings.OPENAI_API_KEY),
        prompt_engineering_available=True,
        features={
            "basic_conversion": True,
            "advanced_prompts": True,
            "openai_integration": bool(settings.OPENAI_API_KEY),
            "rag_chains": True
        }
    )

# 중복 경로 제거 ("/api/health" → 삭제). 헬스체크는 "/health"만 제공합니다.


class DBHealthResponse(BaseModel):
    """DB 상태 응답"""
    connected: bool
    dialect: str
    database: Optional[str] = None
    tables: List[str] = []
    error: Optional[str] = None


@router.get(
    "/db-health",
    response_model=DBHealthResponse,
    summary="데이터베이스 상태 확인",
    description="DATABASE_URL 기준으로 연결 가능 여부와 테이블 목록을 확인합니다."
)
async def db_health() -> DBHealthResponse:
    try:
        db_engine = engine
        with db_engine.connect() as conn:
            insp = inspect(conn)
            tables = insp.get_table_names()
            url = db_engine.url
            return DBHealthResponse(
                connected=True,
                dialect=url.get_backend_name(),
                database=url.database,
                tables=tables,
            )
    except Exception as e:
        try:
            url = engine.url
            dialect = url.get_backend_name()
            database = url.database
        except Exception:
            dialect, database = "unknown", None
        return DBHealthResponse(
            connected=False,
            dialect=dialect,
            database=database,
            tables=[],
            error=str(e),
        )
