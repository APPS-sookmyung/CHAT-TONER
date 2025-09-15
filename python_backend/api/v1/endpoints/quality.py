"""
Text Quality Analysis Endpoints (RAG-based)
RAG를 활용한 텍스트 품질 분석 및 제안 엔드포인트
"""

from fastapi import APIRouter, HTTPException, Depends
import json
import re
import statistics
from typing import Annotated, Dict, List, Any

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

def extract_json_from_text(text: str) -> Dict[str, Any]:
    """텍스트에서 JSON 부분을 추출하고 파싱"""
    try:
        # 첫 번째 시도: 전체 텍스트가 JSON인지 확인
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass
    
    try:
        # 두 번째 시도: ```json 블록 찾기
        json_block_match = re.search(r'```json\s*\n(.*?)\n```', text, re.DOTALL)
        if json_block_match:
            return json.loads(json_block_match.group(1).strip())
    except json.JSONDecodeError:
        pass
    
    try:
        # 세 번째 시도: 중괄호 사이의 JSON 찾기
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            return json.loads(json_str)
    except json.JSONDecodeError:
        pass
    
    raise ValueError("응답에서 유효한 JSON을 찾을 수 없습니다")

def validate_and_normalize_score(score: Any) -> float:
    """점수를 검증하고 0-100 범위로 정규화"""
    try:
        score_float = float(score)
        return max(0.0, min(100.0, score_float))
    except (ValueError, TypeError):
        logger.warning(f"잘못된 점수 형식: {score}, 기본값 50.0 사용")
        return 50.0

def calculate_rag_weighted_score(base_score: float, rag_sources: List[Dict[str, Any]], confidence_factor: float = 1.0) -> float:
    """RAG 검색 결과를 바탕으로 점수에 가중치 적용"""
    if not rag_sources:
        return base_score * 0.7  # RAG 검색 결과가 없으면 신뢰도 감소
    
    # 유사도 점수들 추출
    similarities = []
    for source in rag_sources:
        if 'similarity' in source:
            try:
                sim_score = float(source['similarity'])
                similarities.append(sim_score)
            except (ValueError, TypeError):
                continue
    
    if similarities:
        # 평균 유사도를 가중치로 사용
        avg_similarity = statistics.mean(similarities)
        # 유사도가 높을수록 신뢰도 증가 (0.5-1.2 배율)
        weight_factor = 0.5 + (avg_similarity * 0.7)
        weighted_score = base_score * weight_factor * confidence_factor
        return max(0.0, min(100.0, weighted_score))
    
    return base_score * confidence_factor

def get_fallback_scores(text: str) -> Dict[str, float]:
    """RAG 실패시 기본 휴리스틱 점수 계산"""
    text_length = len(text.strip())
    word_count = len(text.split())
    
    # 기본 점수 계산
    grammar_score = 70.0  # 기본 문법 점수
    if text_length > 100:
        grammar_score += 10.0  # 충분한 길이
    if word_count > 10:
        grammar_score += 5.0   # 충분한 단어 수
    
    # 간단한 격식도 판단 (존댓말 검사)
    formality_score = 60.0
    if any(marker in text for marker in ['습니다', '됩니다', '있습니다']):
        formality_score += 20.0
    
    # 가독성 점수 (문장 길이 기반)
    sentences = text.split('.')
    avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
    if avg_sentence_length < 20:  # 적당한 문장 길이
        readability_score = 75.0
    else:
        readability_score = max(40.0, 75.0 - (avg_sentence_length - 20) * 2)
    
    return {
        'grammarScore': grammar_score,
        'formalityScore': formality_score,
        'readabilityScore': readability_score
    }

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