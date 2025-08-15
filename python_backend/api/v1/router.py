"""
Main API Router
모든 엔드포인트를 통합하는 메인 라우터
"""

from fastapi import APIRouter

# 개별 엔드포인트 라우터들 import
from .endpoints import conversion, health, profile, quality, feedback, rag

# 메인 API 라우터 생성
api_router = APIRouter()

# Health check (루트 레벨)
api_router.include_router(health.router, tags=["health"])

# API v1 엔드포인트들 (중복된 "/api" 프리픽스 제거)
api_router.include_router(conversion.router, prefix="/conversion", tags=["conversion"])
api_router.include_router(profile.router, prefix="/profile", tags=["profile"])
api_router.include_router(quality.router, prefix="/quality", tags=["quality"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
api_router.include_router(rag.router, prefix="/rag", tags=["rag"])