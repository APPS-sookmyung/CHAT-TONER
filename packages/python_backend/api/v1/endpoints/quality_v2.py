from fastapi import APIRouter, HTTPException, Depends
from api.v1.schemas.quality_v2 import QualityRequest, QualityResponse, QualityData, FinalTextRequest, FinalTextResponse
from services.quality_service_v2 import QualityService
from core.state import protocol_retriever
from functools import lru_cache
from typing import Dict, Any

router = APIRouter()


@lru_cache(maxsize=1)
def get_quality_service() -> QualityService:
    return QualityService()


@router.get("/rag-status")
async def get_rag_status() -> Dict[str, Any]:
    """RAG 상태 확인 엔드포인트"""
    return protocol_retriever.get_status()


@router.post("/analyze", response_model=QualityResponse)
async def analyze_quality(
    req: QualityRequest,
    service: QualityService = Depends(get_quality_service),
):
    result = await service.analyze(
        text=req.text,
        target=req.target,
        context=req.context,
        company_id=req.company_id,
    )

    if not result.success:
        raise HTTPException(status_code=422, detail=result.error)

    return QualityResponse(
        success=True,
        data=QualityData(**result.data),
        method_used=result.method_used,
        rag_sources_count=result.rag_sources_count,
        confidence_level=result.confidence_level,
        processing_time=result.processing_time,
    )


@router.post("/generate-final-text")
async def generate_final_text(
    req: FinalTextRequest,
    service: QualityService = Depends(get_quality_service),
):

    ...