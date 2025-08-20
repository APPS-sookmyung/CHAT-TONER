"""
Text Quality Analysis Endpoints (RAG-based)
RAG를 활용한 텍스트 품질 분석 및 제안 엔드포인트
"""

from fastapi import APIRouter, HTTPException, Depends
import json
from typing import Annotated

# RAG 서비스를 사용하도록 의존성 변경
from services.rag_service import RAGService
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

# RAG 서비스 의존성 주입 함수
def get_rag_service():
    """RAG 서비스 인스턴스 생성"""
    try:
        return RAGService()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"RAG 서비스를 사용할 수 없습니다: {str(e)}")

@router.post("/analyze", response_model=QualityAnalysisResponse)
async def analyze_text_quality(
    request: QualityAnalysisRequest,
    rag_service: Annotated[RAGService, Depends(get_rag_service)]
) -> QualityAnalysisResponse:
    """텍스트 품질 분석 (RAG 기반)"""
    try:
        # RAG에 보낼 상세한 프롬프트(질문) 구성
        prompt = f"""'좋은 글쓰기 원칙'과 '문법 규칙' 관련 문서를 참고하여, 아래 텍스트의 품질을 분석해줘.
        
        분석 항목:
        1. 문법 정확도 (grammarScore)
        2. 격식 수준 (formalityScore)
        3. 가독성 (readabilityScore)
        4. 개선 제안 (suggestions) - 2개
        
        반드시 아래 JSON 형식으로만 응답해줘. 다른 설명은 절대 추가하지 마.
        {{
            "grammarScore": <0.0에서 100.0 사이의 점수>,
            "formalityScore": <0.0에서 100.0 사이의 점수>,
            "readabilityScore": <0.0에서 100.0 사이의 점수>,
            "suggestions": [
                {{
                    "original": "개선이 필요한 원본 단어나 구절",
                    "suggestion": "개선된 표현",
                    "reason": "개선 이유"
                }}
            ]
        }}

        --- 분석할 텍스트 ---
        {request.text}
        """
        
        # RAG 서비스 호출 (생성형 답변 함수 사용)
        rag_result = await rag_service.ask_generative_question(query=prompt, context="텍스트 품질 분석")
        
        if not rag_result or not rag_result.get("success"):
            raise HTTPException(status_code=500, detail="RAG 서비스가 품질 분석에 실패했습니다.")

        # RAG의 답변(answer)에 포함된 JSON 문자열을 파싱
        analysis_data = json.loads(rag_result["answer"])
        
        # suggestions를 SuggestionItem 객체로 변환
        suggestions = [SuggestionItem(**s) for s in analysis_data.get("suggestions", [])]
        
        return QualityAnalysisResponse(
            grammarScore=analysis_data["grammarScore"],
            formalityScore=analysis_data["formalityScore"], 
            readabilityScore=analysis_data["readabilityScore"],
            suggestions=suggestions
        )

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="RAG 서비스의 응답(JSON)을 파싱하는 데 실패했습니다.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"품질 분석 중 오류 발생: {str(e)}")


@router.post("/suggestions", response_model=ContextSuggestionsResponse)
async def get_context_suggestions(
    request: ContextSuggestionsRequest,
    rag_service: Annotated[RAGService, Depends(get_rag_service)]
) -> ContextSuggestionsResponse:
    """맥락별 표현 개선 제안 (RAG 기반)"""
    try:
        # RAG에 보낼 상세한 프롬프트(질문) 구성
        prompt = f"""'글쓰기 스타일 가이드' 문서를 참고하여, '{request.context}' 맥락에서 아래 텍스트의 표현을 더 좋게 바꿀 수 있는 제안들을 3개만 찾아줘.
        
        반드시 아래의 JSON 형식으로만 응답해야 해. 다른 설명은 절대 추가하지 마.
        [
          {{
            "original": "개선이 필요한 원본 단어 또는 구절",
            "suggestion": "더 나은 표현 제안",
            "reason": "왜 그렇게 제안하는지에 대한 간단한 이유"
          }}
        ]

        --- 개선할 텍스트 ---
        {request.text}
        """
        
        # RAG 서비스 호출 (생성형 답변 함수 사용)
        rag_result = await rag_service.ask_generative_question(query=prompt, context="표현 개선 제안")

        if not rag_result or not rag_result.get("success"):
            raise HTTPException(status_code=500, detail="RAG 서비스가 표현 제안에 실패했습니다.")

        # RAG의 답변(answer)에 포함된 JSON 문자열을 파싱
        suggestions_list = json.loads(rag_result["answer"])
        
        relevant_suggestions = [SuggestionItem(**s) for s in suggestions_list]

        return ContextSuggestionsResponse(
            suggestions=relevant_suggestions,
            count=len(relevant_suggestions)
        )
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="RAG 서비스의 응답(JSON)을 파싱하는 데 실패했습니다.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"맥락 제안 생성 실패: {str(e)}")