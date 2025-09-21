"""
개선된 텍스트 품질 분석 스키마
맥락별 피드백과 상세 분석을 위한 확장된 데이터 모델
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union, Literal

TargetAudience = Literal[
    "초등학생", "중학생", "고등학생", "대학생", 
    "성인학습자", "교사", "학부모", "일반인"
]

ContextType = Literal["일반", "교육", "보고서_공문"]

ConfidenceLevel = Literal["높음", "보통", "낮음"]

ImprovementCategory = Literal["문법", "격식도", "가독성", "맥락별", "대상별"]

class SuggestionItem(BaseModel):
    """개선 제안 항목"""
    original: str = Field(description="원본 표현")
    suggestion: str = Field(description="개선 제안")
    reason: str = Field(description="개선 이유")
    category: Optional[ImprovementCategory] = Field(default=None, description="개선 카테고리")
    priority: Optional[int] = Field(default=None, description="우선순위 (1-5)")

class QualityAnalysisRequest(BaseModel):
    """텍스트 품질 분석 요청"""
    text: str = Field(description="분석할 텍스트")
    target_audience: TargetAudience = Field(description="대상 청중")
    context: ContextType = Field(description="사용 맥락")

class QualityAnalysisResponse(BaseModel):
    """기본 텍스트 품질 분석 응답"""
    grammarScore: float = Field(description="문법 점수 (0-100)")
    formalityScore: float = Field(description="격식도 점수 (0-100)")
    readabilityScore: float = Field(description="가독성 점수 (0-100)")
    suggestions: List[SuggestionItem] = Field(description="개선 제안 목록")

class ContextSuggestionsRequest(BaseModel):
    """맥락별 제안 요청"""
    text: str = Field(description="분석할 텍스트")
    context: ContextType = Field(description="사용 맥락")

class ContextSuggestionsResponse(BaseModel):
    """맥락별 제안 응답"""
    suggestions: List[SuggestionItem] = Field(description="맥락별 개선 제안")
    count: int = Field(description="제안 개수")

# 새로운 상세 분석 스키마
class TextStatistics(BaseModel):
    """텍스트 기본 통계"""
    character_count: int = Field(description="전체 글자 수")
    character_count_no_spaces: int = Field(description="공백 제외 글자 수")
    word_count: int = Field(description="단어 수")
    sentence_count: int = Field(description="문장 수")
    average_sentence_length: float = Field(description="평균 문장 길이")
    average_word_length: float = Field(description="평균 단어 길이")
    readability_index: str = Field(description="가독성 지수")

class ContextAnalysisDetail(BaseModel):
    """맥락 분석 상세 결과"""
    context_type: ContextType = Field(description="분석된 맥락")
    analysis_details: Dict[str, Any] = Field(description="상세 분석 데이터")
    context_specific_feedback: List[str] = Field(description="맥락별 피드백")
    formality_assessment: Optional[Dict[str, str]] = Field(default=None, description="격식도 평가")

class TargetAnalysisDetail(BaseModel):
    """대상 분석 상세 결과"""
    target_audience: TargetAudience = Field(description="분석된 대상")
    analysis_details: Dict[str, Any] = Field(description="상세 분석 데이터")
    target_specific_feedback: List[str] = Field(description="대상별 피드백")
    vocabulary_appropriateness: Optional[str] = Field(default=None, description="어휘 적절성")
    comprehension_level: Optional[str] = Field(default=None, description="이해 수준")

class RAGAnalysisInfo(BaseModel):
    """RAG 분석 정보"""
    sources_used: int = Field(description="사용된 소스 개수")
    confidence_level: ConfidenceLevel = Field(description="분석 신뢰도")
    search_queries: Optional[List[str]] = Field(default=None, description="사용된 검색 쿼리")

class DetailedAnalysisResponse(BaseModel):
    """상세 분석 응답"""
    basic_scores: Dict[str, float] = Field(description="기본 점수들")
    context_analysis: ContextAnalysisDetail = Field(description="맥락 분석 결과")
    target_analysis: TargetAnalysisDetail = Field(description="대상 분석 결과")
    suggestions: List[SuggestionItem] = Field(description="개선 제안 목록")
    rag_analysis: RAGAnalysisInfo = Field(description="RAG 분석 정보")
    text_statistics: TextStatistics = Field(description="텍스트 통계")
    improvement_priority: List[str] = Field(description="개선 우선순위")

class ContextInfo(BaseModel):
    """맥락 정보"""
    context_type: Union[ContextType, str] = Field(description="맥락 타입")
    name: str = Field(description="맥락 이름")
    description: str = Field(description="맥락 설명")
    scoring_criteria: Dict[str, str] = Field(description="평가 기준")
    example_feedback: str = Field(description="피드백 예시")

class AvailableContextsResponse(BaseModel):
    """사용 가능한 맥락 목록 응답"""
    contexts: List[Dict[str, str]] = Field(description="맥락 목록")
    total_count: int = Field(description="전체 맥락 수")

# 에러 응답 스키마
class QualityAnalysisError(BaseModel):
    """품질 분석 에러 응답"""
    error_code: str = Field(description="에러 코드")
    error_message: str = Field(description="에러 메시지")
    fallback_used: bool = Field(description="Fallback 사용 여부")
    suggestions: Optional[List[SuggestionItem]] = Field(default=None, description="Fallback 제안")