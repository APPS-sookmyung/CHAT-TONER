"""
Text Quality Analysis Endpoints
텍스트 품질 분석 엔드포인트
"""

from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends
from dependency_injector.wiring import inject, Provide
import re

from core.container import Container
from services.openai_services import OpenAIService
from api.v1.schemas.quality import (
    QualityAnalysisRequest,
    QualityAnalysisResponse,
    ContextSuggestionsRequest,
    ContextSuggestionsResponse,
    SuggestionItem
)
import logging

logger = logging.getLogger('chattoner')

router = APIRouter()

@router.post("/analyze-quality", response_model=QualityAnalysisResponse)
@inject
async def analyze_text_quality(
    request: QualityAnalysisRequest,
    openai_service: Annotated[
        OpenAIService,
        Depends(Provide[Container.openai_service])
    ]
) -> QualityAnalysisResponse:
    """텍스트 품질 분석"""
    try:
        text = request.text
        
        # 기본 품질 분석 로직
        word_count = len(text.split())
        sentence_count = len([s for s in text.split('.') if s.strip()])
        
        # 정중한 표현 패턴 검사
        polite_patterns = [r'습니다$', r'해주세요$', r'부탁드립니다$', r'감사합니다$']
        has_polite_endings = any(re.search(pattern, text) for pattern in polite_patterns)
        
        # 업무 용어 검사
        business_terms = ['보고서', '회의', '검토', '승인', '협의', '논의', '진행', '완료']
        has_business_terms = any(term in text for term in business_terms)
        
        # 점수 계산
        grammar_score = min(95.0, 80.0 + (len(text) / 10))  # 기본 80점 + 텍스트 길이 보너스
        formality_score = 90.0 if has_polite_endings else 65.0
        readability_score = 90.0 if word_count < 50 else max(70.0, 90.0 - (word_count - 50) * 0.5)
        
        # 개선 제안 생성
        suggestions = []
        if word_count > 50:
            suggestions.append("문장을 더 짧게 나누어 가독성을 높여보세요")
        if not has_polite_endings:
            suggestions.append("좀 더 정중한 표현을 사용해보세요")
        if has_business_terms:
            suggestions.append("적절한 업무 용어를 사용하고 계십니다")
        else:
            suggestions.append("맥락에 맞는 전문 용어 사용을 고려해보세요")
        
        if sentence_count > 5:
            suggestions.append("긴 문단을 여러 개의 짧은 문단으로 나누는 것을 고려해보세요")
            
        return QualityAnalysisResponse(
            grammarScore=grammar_score,
            formalityScore=formality_score,
            readabilityScore=readability_score,
            suggestions=suggestions
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"품질 분석 실패: {str(e)}")

@router.post("/context-suggestions", response_model=ContextSuggestionsResponse)
@inject
async def get_context_suggestions(
    request: ContextSuggestionsRequest,
    openai_service: Annotated[
        OpenAIService,
        Depends(Provide[Container.openai_service])
    ]
) -> ContextSuggestionsResponse:
    """맥락별 표현 개선 제안"""
    try:
        context = request.context
        text = request.text
        
        # 맥락별 제안 데이터베이스
        suggestion_database = {
            "business": [
                {"original": "확인", "suggestion": "검토", "reason": "업무상 더 정확한 표현"},
                {"original": "해주세요", "suggestion": "부탁드립니다", "reason": "비즈니스 매너"},
                {"original": "빨리", "suggestion": "신속히", "reason": "전문적인 표현"},
                {"original": "좋다", "suggestion": "적절하다", "reason": "객관적 평가 표현"}
            ],
            "casual": [
                {"original": "확인해주세요", "suggestion": "한번 봐주세요", "reason": "친근한 표현"},
                {"original": "검토", "suggestion": "체크", "reason": "일상적 표현"},
                {"original": "부탁드립니다", "suggestion": "부탁해요", "reason": "캐주얼한 톤"},
                {"original": "진행하겠습니다", "suggestion": "해볼게요", "reason": "자연스러운 표현"}
            ],
            "report": [
                {"original": "많이", "suggestion": "상당히", "reason": "공식 문서 표현"},
                {"original": "좋다", "suggestion": "양호하다", "reason": "보고서 적합 표현"},
                {"original": "빨리", "suggestion": "조속히", "reason": "공문서 표현"},
                {"original": "문제", "suggestion": "이슈", "reason": "전문 용어"}
            ]
        }
        
        # 맥락에 맞는 제안 선택
        suggestions = suggestion_database.get(context, suggestion_database["business"])
        
        # 텍스트에 실제로 포함된 단어들과 매칭되는 제안만 필터링
        relevant_suggestions = []
        for suggestion in suggestions:
            if suggestion["original"] in text:
                relevant_suggestions.append(SuggestionItem(**suggestion))
        
        # 관련 제안이 없으면 기본 제안 제공
        if not relevant_suggestions:
            relevant_suggestions = [SuggestionItem(**s) for s in suggestions[:2]]
        
        return ContextSuggestionsResponse(
            suggestions=relevant_suggestions,
            count=len(relevant_suggestions)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"맥락 제안 생성 실패: {str(e)}")