"""
Main API Router
모든 엔드포인트를 통합하는 메인 라우터
"""

from fastapi import APIRouter

# 개별 엔드포인트 라우터들 import
from .endpoints import conversion, health, profile, feedback, rag, documents, quality, company_profile


# from .endpoints import quality, company  # Temporarily disabled due to langgraph dependency
# 새로운 엔드포인트들 조건부 import
try:
    from .endpoints import surveys, kb, suggest # Uncommented
    NEW_ENDPOINTS_AVAILABLE = True # Changed to True
except ImportError:
    NEW_ENDPOINTS_AVAILABLE = False

from ..company_survey import router as company_survey_router

# 메인 API 라우터 생성
api_router = APIRouter()

# Health check (루트 레벨)
api_router.include_router(health.router, tags=["health"])

# API v1 엔드포인트들 (중복된 "/api" 프리픽스 제거)
api_router.include_router(conversion.router, prefix="/conversion", tags=["conversion"])
api_router.include_router(profile.router, prefix="/profile", tags=["profile"])
api_router.include_router(quality.router, prefix="/quality", tags=["quality"])  # enabled with LLM fallbacks
api_router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
api_router.include_router(rag.router, prefix="/rag", tags=["rag"])

# api_router.include_router(company.router, prefix="/company", tags=["company"])  # Temporarily disabled
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(company_survey_router, tags=["company_survey"])
api_router.include_router(company_profile.router, prefix="/company-profile", tags=["company_profile"])

# 새로운 엔드포인트들 추가 (조건부)
if NEW_ENDPOINTS_AVAILABLE:
    api_router.include_router(surveys.router, prefix="/surveys", tags=["surveys"])
    api_router.include_router(kb.router, prefix="/kb", tags=["knowledge_base"])
    api_router.include_router(suggest.router, prefix="/suggest", tags=["suggestions"])
