# api/v1/schemas/quality.py

from pydantic import BaseModel, Field
from typing import Optional, List


class IssueItem(BaseModel):
    severity: str
    location: str
    description: str
    suggestion: str


class SectionResult(BaseModel):
    score: float
    justification: str
    issues: List[IssueItem]
    markdown_explanation: str  # ← 추가


class QualityData(BaseModel):
    grammar: SectionResult
    formality: SectionResult
    protocol: SectionResult
    final_text: str
    final_text_warning: Optional[str] = None
    summary: str


class QualityRequest(BaseModel):
    text: str = Field(..., min_length=1)
    target: str
    context: str
    company_id: Optional[str] = None


class QualityResponse(BaseModel):
    success: bool
    data: Optional[QualityData] = None
    error: Optional[str] = None
    method_used: str
    rag_sources_count: int
    confidence_level: str
    processing_time: float

class FinalTextRequest(BaseModel):
    original_text: str = Field(..., min_length=1)
    target: str
    context: str
    grammar_feedback: Optional[str] = None
    formality_feedback: Optional[str] = None
    protocol_feedback: Optional[str] = None


class FinalTextResponse(BaseModel):
    final_text: str
    processing_time: float