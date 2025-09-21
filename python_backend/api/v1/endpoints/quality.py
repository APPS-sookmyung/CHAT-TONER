"""
최종 통합된 텍스트 품질 분석 엔드포인트
LangGraph Agent + RAG + Fallback 시스템 완전 통합
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Annotated, Dict, List, Any, Optional
import logging
import asyncio

from services.rag_service import RAGService
from services.quality_analysis_service import create_quality_analysis_service, monitor_performance
from api.v1.schemas.quality import (
    QualityAnalysisRequest,
    QualityAnalysisResponse,
    ContextSuggestionsRequest,
    ContextSuggestionsResponse,
    DetailedAnalysisResponse,
    ContextInfo,
    AvailableContextsResponse,
    SuggestionItem,
    TargetAudience,
    ImprovementCategory
)
from agents.quality_analysis_agent import CONTEXT_CONFIGS

logger = logging.getLogger('chattoner')
router = APIRouter()

def get_rag_service():
    """RAG 서비스 인스턴스"""
    try:
        return RAGService()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"RAG 서비스를 사용할 수 없습니다: {str(e)}")

def get_quality_service(rag_service: Annotated[RAGService, Depends(get_rag_service)]):
    """품질 분석 서비스 인스턴스"""
    try:
        return create_quality_analysis_service(
            rag_service=rag_service,
            enable_agent=True,
            fallback_enabled=True
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"품질 분석 서비스를 초기화할 수 없습니다: {str(e)}")

@router.post("/analyze", response_model=QualityAnalysisResponse)
@monitor_performance
async def analyze_text_quality(
    request: QualityAnalysisRequest,
    quality_service: Annotated[Any, Depends(get_quality_service)]
) -> QualityAnalysisResponse:
    """
    통합 텍스트 품질 분석
    - LangGraph Agent 우선 사용
    - RAG 기반 맥락별/대상별 분석
    - Fallback 시스템으로 안정성 보장
    """
    
    try:
        logger.info(f"품질 분석 요청 - 대상: {request.target_audience}, 맥락: {request.context}, 텍스트 길이: {len(request.text)}")
        
        # 빈 텍스트/ 길이 제한 검사
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="분석할 텍스트가 비어있습니다.")
        
        if len(request.text) > 5000:
            raise HTTPException(status_code=400, detail="텍스트가 너무 깁니다. (최대 5000자)")
        
        # 통합 서비스를 통한 분석 실행
        analysis_result = await quality_service.analyze_text_quality(
            text=request.text,
            target_audience=request.target_audience,
            context=request.context,
            detailed=False
        )
        
        # 결과 변환
        suggestions = []
        for sugg in analysis_result.get("suggestions", []):
            category = sugg.get("category")
            valid_categories = ["문법", "격식도", "가독성", "맥락별", "대상별", "일반"]
            
            suggestions.append(SuggestionItem(
                original=sugg.get("original", ""),
                suggestion=sugg.get("suggestion", ""),
                reason=sugg.get("reason", ""),
                category=category if category in valid_categories else None,
                priority=sugg.get("priority")
            ))
        
        response = QualityAnalysisResponse(
            grammarScore=round(analysis_result.get("grammar_score", 65.0), 1),
            formalityScore=round(analysis_result.get("formality_score", 65.0), 1),
            readabilityScore=round(analysis_result.get("readability_score", 65.0), 1),
            suggestions=suggestions
        )
        
        # 성능 로깅
        method_used = analysis_result.get("method_used", "unknown")
        processing_time = analysis_result.get("processing_time", 0)
        
        logger.info(f"품질 분석 완료 - 방법: {method_used}, 소요시간: {processing_time:.2f}초, "
                   f"점수: G{response.grammarScore}/F{response.formalityScore}/R{response.readabilityScore}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"품질 분석 중 예기치 못한 오류: {e}")
        raise HTTPException(status_code=500, detail="분석 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.")

@router.post("/detailed-analysis", response_model=DetailedAnalysisResponse)
@monitor_performance
async def get_detailed_analysis(
    request: QualityAnalysisRequest,
    quality_service: Annotated[Any, Depends(get_quality_service)]
) -> DetailedAnalysisResponse:
    """
    상세 텍스트 품질 분석
    - 모든 단계별 분석 결과 제공
    - 텍스트 통계 및 개선 우선순위 포함
    - RAG 분석 정보 제공
    """
    
    try:
        logger.info(f"상세 분석 요청 - 대상: {request.target_audience}, 맥락: {request.context}")
        
        # 상세 분석 실행
        analysis_result = await quality_service.analyze_text_quality(
            text=request.text,
            target_audience=request.target_audience,
            context=request.context,
            detailed=True
        )
        
        # 상세 응답 구성
        suggestions = []
        for sugg in analysis_result.get("suggestions", []):
            category = sugg.get("category")
            valid_categories = ["문법", "격식도", "가독성", "맥락별", "대상별", "일반"]
            
            suggestions.append(SuggestionItem(
                original=sugg.get("original", ""),
                suggestion=sugg.get("suggestion", ""),
                reason=sugg.get("reason", ""),
                category=category if category in valid_categories else None,
                priority=sugg.get("priority")
            ))
        
        detailed_response = {
            "basic_scores": {
                "grammar_score": analysis_result.get("grammar_score", 65.0),
                "formality_score": analysis_result.get("formality_score", 65.0),
                "readability_score": analysis_result.get("readability_score", 65.0)
            },
            "context_analysis": {
                "context_type": request.context,
                "analysis_details": analysis_result.get("context_analysis", {}),
                "context_specific_feedback": analysis_result.get("context_feedback", [])
            },
            "target_analysis": {
                "target_audience": request.target_audience,
                "analysis_details": analysis_result.get("target_analysis", {}),
                "target_specific_feedback": analysis_result.get("target_feedback", [])
            },
            "suggestions": suggestions,
            "rag_analysis": {
                "sources_used": analysis_result.get("rag_sources_count", 0),
                "confidence_level": analysis_result.get("confidence_level", "낮음")
            },
            "text_statistics": analysis_result.get("text_statistics", {}),
            "improvement_priority": analysis_result.get("improvement_priority", [])
        }
        
        return detailed_response
        
    except Exception as e:
        logger.error(f"상세 분석 실패: {e}")
        raise HTTPException(status_code=500, detail=f"상세 분석 중 오류가 발생했습니다: {str(e)}")

@router.post("/suggestions", response_model=ContextSuggestionsResponse)
@monitor_performance
async def get_context_suggestions(
    request: ContextSuggestionsRequest,
    quality_service: Annotated[Any, Depends(get_quality_service)]
) -> ContextSuggestionsResponse:
    """
    맥락별 표현 개선 제안
    - 맥락 특성에 맞는 전용 피드백
    - RAG 기반 개선 제안
    - 맥락별 피드백 템플릿 적용
    """
    
    try:
        logger.info(f"맥락별 제안 요청 - 맥락: {request.context}, 텍스트 길이: {len(request.text)}")
        
        # 맥락별 제안 생성
        suggestions_result = await quality_service.get_context_suggestions(
            text=request.text,
            context=request.context
        )
        
        # 결과 변환
        suggestions = []
        for sugg in suggestions_result.get("suggestions", []):
            category = sugg.get("category")
            valid_categories = ["문법", "격식도", "가독성", "맥락별", "대상별", "일반"]
            
            suggestions.append(SuggestionItem(
                original=sugg.get("original", ""),
                suggestion=sugg.get("suggestion", ""),
                reason=sugg.get("reason", ""),
                category=category if category in valid_categories else None
            ))
        
        return ContextSuggestionsResponse(
            suggestions=suggestions,
            count=len(suggestions)
        )
        
    except Exception as e:
        logger.error(f"맥락별 제안 생성 실패: {e}")
        raise HTTPException(status_code=500, detail=f"제안 생성 중 오류가 발생했습니다: {str(e)}")

@router.get("/context-info/{context_type}", response_model=ContextInfo)
async def get_context_information(context_type: str) -> ContextInfo:
    """맥락별 상세 정보 제공"""
    
    try:
        
        context_config = CONTEXT_CONFIGS.get(context_type)
        if not context_config:
            raise HTTPException(status_code=404, detail=f"'{context_type}' 맥락을 찾을 수 없습니다.")
        
        return ContextInfo(
            context_type=context_type,  # context_enum,
            name=context_config.name,
            description=context_config.description,
            scoring_criteria=context_config.scoring_criteria,
            example_feedback=context_config.feedback_template.format(
                original="예시 표현",
                reason="개선이 필요한 이유",
                suggestion="개선된 표현"
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"맥락 정보 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="맥락 정보를 가져오는데 실패했습니다.")

@router.get("/available-contexts", response_model=AvailableContextsResponse)
async def get_available_contexts() -> AvailableContextsResponse:
    """사용 가능한 모든 맥락 목록 반환"""
    
    contexts = []
    
    for context_key, config in CONTEXT_CONFIGS.items():
        contexts.append({
            "type": context_key,
            "name": config.name,
            "description": config.description
        })
    
    return AvailableContextsResponse(
        contexts=contexts,
        total_count=len(contexts)
    )

@router.get("/health")
async def health_check(
    rag_service: Annotated[RAGService, Depends(get_rag_service)]
) -> Dict[str, Any]:
    
    try:
        # RAG 서비스 상태 확인
        test_query = "시스템 테스트"
        rag_status = await rag_service.ask_generative_question(
            query=test_query,
            context="상태 확인"
        )
        
        rag_healthy = rag_status and rag_status.get("success", False)
        
        return {
            "status": "healthy" if rag_healthy else "degraded",
            "timestamp": asyncio.get_event_loop().time(),
            "services": {
                "rag_service": "healthy" if rag_healthy else "unhealthy",
                "quality_agent": "healthy",
                "fallback_system": "healthy"
            },
            "version": "1.0.0"
        }
        
    except Exception as e:
        logger.error(f"상태 확인 실패: {e}")
        return {
            "status": "unhealthy",
            "timestamp": asyncio.get_event_loop().time(),
            "error": str(e)
        }