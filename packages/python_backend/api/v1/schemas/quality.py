"""
기업용 품질분석 Pydantic 스키마
기존 schemas/quality.py에 추가할 스키마들
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

# 기업용 열거형
class TargetAudience(str, Enum):
    """대상 열거형"""
    DIRECT_SUPERVISOR = "직속상사"
    TEAMMATE = "팀동료"
    OTHER_DEPARTMENT = "타부서담당자"
    CLIENT = "클라이언트"
    EXTERNAL_PARTNER = "외부협력업체"
    JUNIOR_EMPLOYEE = "후배신입"

class ContextType(str, Enum):
    """상황 열거형"""
    REPORT = "보고서"
    MEETING_MINUTES = "회의록"
    EMAIL = "이메일"
    ANNOUNCEMENT = "공지사항"
    MESSAGE = "메시지"

class FeedbackType(str, Enum):
    """피드백 타입"""
    GRAMMAR = "grammar"
    PROTOCOL = "protocol"

class FeedbackValue(str, Enum):
    """피드백 값"""
    GOOD = "good"
    BAD = "bad"

class SeverityLevel(str, Enum):
    """심각도 레벨"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

# 기업용 제안 아이템
class CompanySuggestionItem(BaseModel):
    """기업용 제안 아이템"""
    id: str = Field(..., description="제안 고유 ID")
    category: str = Field(..., description="제안 카테고리 (문법/프로토콜/톤앤매너)")
    original: str = Field(..., description="원본 표현")
    suggestion: str = Field(..., description="개선 제안")
    reason: str = Field(..., description="개선 이유")
    severity: SeverityLevel = Field(default=SeverityLevel.MEDIUM, description="심각도")

# 섹션별 결과
class GrammarSection(BaseModel):
    """문법 섹션 결과"""
    score: float = Field(..., ge=0, le=100, description="문법 종합 점수")
    suggestions: List[CompanySuggestionItem] = Field(default=[], description="문법 관련 제안들")

class ProtocolSection(BaseModel):
    """프로토콜 섹션 결과"""
    score: float = Field(..., ge=0, le=100, description="프로토콜 준수 점수")
    suggestions: List[CompanySuggestionItem] = Field(default=[], description="프로토콜 관련 제안들")

class CompanyAnalysis(BaseModel):
    """기업 분석 메타데이터"""
    companyId: str = Field(..., description="기업 ID")
    communicationStyle: str = Field(..., description="기업 커뮤니케이션 스타일")
    complianceLevel: float = Field(..., ge=0, le=100, description="전체 준수도")
    methodUsed: str = Field(..., description="사용된 분석 방법")
    processingTime: float = Field(..., description="처리 시간(초)")
    ragSourcesCount: int = Field(default=0, description="참조한 RAG 소스 개수")

# 요청 스키마들
class CompanyQualityAnalysisRequest(BaseModel):
    """기업용 품질분석 요청"""
    text: str = Field(..., min_length=1, max_length=5000, description="분석할 텍스트")
    target_audience: TargetAudience = Field(..., description="대상")
    context: ContextType = Field(..., description="상황/맥락")
    company_id: str = Field(..., description="기업 ID")
    user_id: str = Field(..., description="사용자 ID")
    detailed: bool = Field(default=False, description="상세 분석 여부")

class UserFeedbackRequest(BaseModel):
    """사용자 피드백 요청"""
    user_id: str = Field(..., description="사용자 ID")
    company_id: str = Field(..., description="기업 ID")
    session_id: str = Field(..., description="세션 ID")
    original_text: str = Field(..., description="원본 텍스트")
    suggested_text: str = Field(..., description="제안된 텍스트")
    feedback_type: FeedbackType = Field(..., description="피드백 타입")
    feedback_value: FeedbackValue = Field(..., description="피드백 값")
    target_audience: TargetAudience = Field(..., description="대상")
    context: ContextType = Field(..., description="상황")
    suggestion_category: str = Field(..., description="제안 카테고리")
    scores: Optional[Dict[str, float]] = Field(default=None, description="관련 점수들")

class FinalTextGenerationRequest(BaseModel):
    """최종 통합본 생성 요청"""
    original_text: str = Field(..., description="원본 텍스트")
    grammar_suggestions: List[CompanySuggestionItem] = Field(..., description="문법 제안들")
    protocol_suggestions: List[CompanySuggestionItem] = Field(..., description="프로토콜 제안들")
    selected_grammar_ids: List[str] = Field(default=[], description="선택된 문법 제안 ID들")
    selected_protocol_ids: List[str] = Field(default=[], description="선택된 프로토콜 제안 ID들")
    user_id: str = Field(..., description="사용자 ID")
    company_id: str = Field(..., description="기업 ID")

# 응답 스키마들
class CompanyQualityAnalysisResponse(BaseModel):
    """기업용 품질분석 응답"""
    # 기본 점수들 (기존 호환성)
    grammarScore: float = Field(..., ge=0, le=100, description="문법 점수")
    formalityScore: float = Field(..., ge=0, le=100, description="격식도 점수")
    readabilityScore: float = Field(..., ge=0, le=100, description="가독성 점수")
    
    # 기업용 추가 점수들
    protocolScore: float = Field(..., ge=0, le=100, description="프로토콜 준수 점수")
    complianceScore: float = Field(..., ge=0, le=100, description="전체 컴플라이언스 점수")
    
    # 섹션별 결과 (프론트엔드 표시용)
    grammarSection: GrammarSection = Field(..., description="문법 섹션")
    protocolSection: ProtocolSection = Field(..., description="프로토콜 섹션")
    
    # 메타데이터
    companyAnalysis: CompanyAnalysis = Field(..., description="기업 분석 정보")

class UserFeedbackResponse(BaseModel):
    """사용자 피드백 응답"""
    success: bool = Field(..., description="성공 여부")
    message: str = Field(..., description="응답 메시지")
    session_id: str = Field(..., description="세션 ID")

class AppliedSuggestions(BaseModel):
    """적용된 제안사항 정보"""
    grammarCount: int = Field(..., description="적용된 문법 제안 개수")
    protocolCount: int = Field(..., description="적용된 프로토콜 제안 개수")
    totalApplied: int = Field(..., description="총 적용된 제안 개수")

class FinalTextGenerationResponse(BaseModel):
    """최종 통합본 생성 응답"""
    success: bool = Field(..., description="성공 여부")
    finalText: str = Field(..., description="최종 생성된 텍스트")
    appliedSuggestions: AppliedSuggestions = Field(..., description="적용된 제안사항 정보")
    originalLength: int = Field(..., description="원본 텍스트 길이")
    finalLength: int = Field(..., description="최종 텍스트 길이")
    message: str = Field(..., description="결과 메시지")

# 기업 상태 관련 스키마들
class CompanyStatus(BaseModel):
    """기업 상태 정보"""
    company_id: str = Field(..., description="기업 ID")
    status: str = Field(..., description="상태 (ready/incomplete/error)")
    profile_exists: bool = Field(..., description="프로필 존재 여부")
    guidelines_count: int = Field(..., description="가이드라인 문서 개수")
    company_name: Optional[str] = Field(None, description="기업명")
    communication_style: Optional[str] = Field(None, description="커뮤니케이션 스타일")
    ready_for_analysis: bool = Field(..., description="분석 준비 완료 여부")

class TestSetupResponse(BaseModel):
    """테스트 설정 응답"""
    success: bool = Field(..., description="성공 여부")
    message: str = Field(..., description="응답 메시지")
    company_id: Optional[str] = Field(None, description="생성된 기업 ID")
    status: Optional[Dict[str, Any]] = Field(None, description="기업 상태 정보")
    error: Optional[str] = Field(None, description="오류 메시지")

# 프론트엔드에서 사용할 드롭다운 옵션들
class DropdownOptions(BaseModel):
    """드롭다운 선택 옵션들"""
    target_audiences: List[Dict[str, str]] = Field(
        default=[
            {"value": "직속상사", "label": "직속상사"},
            {"value": "팀동료", "label": "팀동료"},
            {"value": "타부서담당자", "label": "타부서 담당자"},
            {"value": "클라이언트", "label": "클라이언트"},
            {"value": "외부협력업체", "label": "외부 협력업체"},
            {"value": "후배신입", "label": "후배/신입"}
        ],
        description="대상 선택 옵션들"
    )
    
    contexts: List[Dict[str, str]] = Field(
        default=[
            {"value": "보고서", "label": "보고서"},
            {"value": "회의록", "label": "회의록"},
            {"value": "이메일", "label": "이메일"},
            {"value": "공지사항", "label": "공지사항"},
            {"value": "메시지", "label": "메시지"}
        ],
        description="상황 선택 옵션들"
    )

# 개발/테스트용 스키마들
class AnalysisDebugInfo(BaseModel):
    """분석 디버그 정보"""
    api_calls_used: int = Field(..., description="사용된 API 호출 수")
    rag_sources_used: List[str] = Field(default=[], description="사용된 RAG 소스들")
    processing_steps: List[str] = Field(default=[], description="처리 단계들")
    confidence_scores: Dict[str, float] = Field(default={}, description="신뢰도 점수들")
    fallback_reason: Optional[str] = Field(None, description="fallback 사용 이유")

class DetailedCompanyQualityResponse(CompanyQualityAnalysisResponse):
    """상세 분석 정보 포함 응답 (detailed=true일 때)"""
    debugInfo: Optional[AnalysisDebugInfo] = Field(None, description="디버그 정보")
    enterpriseAnalysis: Optional[Dict[str, Any]] = Field(None, description="기업 상세 분석")
    usageRecommendations: Optional[Dict[str, List[str]]] = Field(None, description="사용 권장사항")


# 에러 응답 스키마
class CompanyErrorResponse(BaseModel):
    """기업용 에러 응답"""
    error: str = Field(..., description="에러 메시지")
    error_code: Optional[str] = Field(None, description="에러 코드")
    details: Optional[Dict[str, Any]] = Field(None, description="상세 정보")
    fallback_available: bool = Field(default=True, description="fallback 이용 가능 여부")