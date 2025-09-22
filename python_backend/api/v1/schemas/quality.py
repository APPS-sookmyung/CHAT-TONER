"""
Quality Analysis Schemas
품질 분석 관련 스키마
"""

from typing import List, Dict, Any
from pydantic import BaseModel

class QualityAnalysisRequest(BaseModel):
    text: str
    target_audience: str = "일반인"  # 초등학생, 중학생, 고등학생, 대학생, 성인학습자, 교사, 학부모, 일반인
    context: str = "일반"  # 선택사항: 교육, 보고서, 공문, 일반

class SuggestionItem(BaseModel):
    original: str
    suggestion: str
    reason: str

class QualityAnalysisResponse(BaseModel):
    grammarScore: float
    formalityScore: float
    readabilityScore: float
    suggestions: List[SuggestionItem]

class ContextSuggestionsRequest(BaseModel):
    text: str
    context: str  # business, casual, report

class ContextSuggestionsResponse(BaseModel):
    suggestions: List[SuggestionItem]
    count: int