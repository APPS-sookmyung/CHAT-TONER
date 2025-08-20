"""
Quality Analysis Schemas
품질 분석 관련 스키마
"""

from typing import List, Dict, Any
from pydantic import BaseModel

class QualityAnalysisRequest(BaseModel):
    text: str

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