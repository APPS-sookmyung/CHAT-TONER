"""
Text Quality Analysis Endpoints (기업용 확장)
하드코딩 제거, 명확한 에러 처리
"""

# Standard library imports
import json
import logging
import time
from typing import Annotated, Dict, Any

# Third-party imports
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks

# Local imports - Core services
from services.rag_service import RAGService
from services.rewrite_service import rewrite_text

# Local imports - Schemas
from api.v1.schemas.quality import (
    CompanyQualityAnalysisRequest,
    CompanyQualityAnalysisResponse,
    UserFeedbackRequest,
    UserFeedbackResponse,
    FinalTextGenerationRequest,
    FinalTextGenerationResponse,
    CompanySuggestionItem,
    GrammarSection,
    ProtocolSection,
    CompanyAnalysis,
    DropdownOptions
)
from api.v1.schemas.suggest import FeedbackItem

# Conditional imports for enterprise features
try:
    from agents.quality_analysis_agent import OptimizedEnterpriseQualityAgent
    ENTERPRISE_AGENT_AVAILABLE = True
except ImportError:
    OptimizedEnterpriseQualityAgent = None
    ENTERPRISE_AGENT_AVAILABLE = False

try:
    from services.enterprise_db_service import get_enterprise_db_service, EnterpriseDBService
    ENTERPRISE_DB_AVAILABLE = True
except ImportError:
    get_enterprise_db_service = None
    EnterpriseDBService = None
    ENTERPRISE_DB_AVAILABLE = False

# Logger setup
logger = logging.getLogger('chattoner')
router = APIRouter()


# Dependency injection functions
def get_rag_service():
    """RAG 서비스 싱글톤 인스턴스 반환"""
    from core.container import Container
    container = Container()
    return container.rag_service()


def get_enterprise_quality_agent():
    """기업용 품질분석 Agent 싱글톤 인스턴스 반환"""
    if not ENTERPRISE_AGENT_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="기업용 기능이 비활성화되어 있습니다. langgraph 의존성을 설치해주세요."
        )

    from core.container import Container
    container = Container()
    return container.enterprise_quality_agent()


async def get_enterprise_db_service_dep():
    """기업용 DB 서비스 의존성"""
    if not ENTERPRISE_DB_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="기업용 DB 기능이 비활성화되어 있습니다. asyncpg 의존성을 설치해주세요."
        )
    return await get_enterprise_db_service()


@router.get("/company/options", response_model=DropdownOptions)
async def get_dropdown_options() -> DropdownOptions:
    """프론트엔드 드롭다운 옵션 제공"""
    return DropdownOptions()


@router.post("/company/analyze", response_model=CompanyQualityAnalysisResponse)
async def analyze_company_text_quality(
    request: CompanyQualityAnalysisRequest,
    agent: Annotated[object, Depends(get_enterprise_quality_agent)]
) -> CompanyQualityAnalysisResponse:
   
    start_time = time.time()

    try:
        logger.info(
            f"기업용 품질분석 시작 - 회사: {request.company_id}, "
            f"대상: {request.target_audience.value}, 상황: {request.context.value}"
        )

        # Agent 직접 호출
        result = await agent.analyze_enterprise_quality(
            text=request.text,
            target_audience=request.target_audience.value,
            context=request.context.value,
            company_id=request.company_id,
            user_id=request.user_id
        )
        
        # 에러 체크
        if result.get('error'):
            error_msg = result.get('error')
            logger.error(f"분석 실패: {error_msg}")
            
            # 기업 프로필 관련 에러는 400
            if 'company' in error_msg.lower() or 'profile' in error_msg.lower():
                raise HTTPException(
                    status_code=400,
                    detail="기업 프로필 설정 필요"
                )
            
            # 기타 에러는 500
            raise HTTPException(
                status_code=500,
                detail=f"분석 실패: {error_msg}"
            )
        
        # 점수 검증 (0점이면 분석 실패로 간주)
        grammar_score = result.get('grammar_score', 0.0)
        if grammar_score == 0.0:
            logger.error("분석 결과가 비어있음")
            raise HTTPException(
                status_code=500,
                detail="분석 실패: 점수 계산 불가"
            )
        
        # Agent 결과를 API 응답 형식으로 변환
        response = CompanyQualityAnalysisResponse(
            # 기본 점수들
            grammarScore=result['grammar_score'],
            formalityScore=result['formality_score'],
            readabilityScore=result['readability_score'],
            protocolScore=result['protocol_score'],
            complianceScore=result['compliance_score'],
            
            # 섹션별 결과
            grammarSection=GrammarSection(
                score=result['grammar_score'],
                suggestions=[
                    CompanySuggestionItem(
                        id=f"grammar_{i}",
                        category=sugg.get('category', 'grammar'),
                        original=sugg.get('original', ''),
                        suggestion=sugg.get('suggestion', ''),
                        reason=sugg.get('reason', ''),
                        severity='medium'
                    )
                    for i, sugg in enumerate(result.get('suggestions', []))
                ]
            ),
            
            protocolSection=ProtocolSection(
                score=result['protocol_score'],
                suggestions=[
                    CompanySuggestionItem(
                        id=f"protocol_{i}",
                        category=sugg.get('category', 'protocol'),
                        original=sugg.get('violation', sugg.get('rule', '')),
                        suggestion=sugg.get('correction', sugg.get('suggestion', '')),
                        reason=sugg.get('reason', '') or sugg.get('rule', ''),
                        severity=sugg.get('severity', 'medium')
                    )
                    for i, sugg in enumerate(result.get('protocol_suggestions', []))
                ]
            ),
            
            # 메타데이터
            companyAnalysis=CompanyAnalysis(
                companyId=request.company_id,
                communicationStyle=result.get('company_analysis', {}).get('communication_style', 'formal'),
                complianceLevel=result['compliance_score'],
                methodUsed=result.get('optimization_info', {}).get('analysis_method', 'comprehensive'),
                processingTime=result.get('processing_time', 0.0),
                ragSourcesCount=result.get('rag_sources_count', 0)
            )
        )
        
        # 성능 로깅
        execution_time = time.time() - start_time
        logger.info(f"기업용 분석 완료 - 실행시간: {execution_time:.2f}초")

        if execution_time > 5.0:
            logger.warning(
                f"느린 품질분석 호출 감지: {execution_time:.2f}초 "
                f"(텍스트 길이: {len(request.text)})"
            )

        return response

    except HTTPException:
        raise
    
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"기업용 품질분석 실패 ({execution_time:.2f}초): {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"기업용 품질분석 실패: {str(e)}")


@router.post("/company/feedback", response_model=UserFeedbackResponse)
async def save_user_feedback(
    request: UserFeedbackRequest,
    background_tasks: BackgroundTasks,
    db_service: Annotated[object, Depends(get_enterprise_db_service_dep)]
) -> UserFeedbackResponse:
    try:
        logger.info(
            f"사용자 피드백 저장 - 세션: {request.session_id}, "
            f"타입: {request.feedback_type.value}"
        )
        
        # 피드백 데이터 구성
        feedback_data = {
            'user_id': request.user_id,
            'company_id': request.company_id,
            'session_id': request.session_id,
            'original_text': request.original_text,
            'suggested_text': request.suggested_text,
            'feedback_type': request.feedback_type.value,
            'feedback_value': request.feedback_value.value,
            'metadata': {
                'target_audience': request.target_audience.value,
                'context': request.context.value,
                'suggestion_category': request.suggestion_category,
                'scores': request.scores
            }
        }
        
        # 백그라운드에서 DB에 저장
        background_tasks.add_task(db_service.save_user_feedback, feedback_data)
        
        return UserFeedbackResponse(
            success=True,
            message="피드백이 성공적으로 저장되었습니다",
            session_id=request.session_id
        )
        
    except Exception as e:
        logger.error(f"사용자 피드백 저장 중 오류: {e}")
        return UserFeedbackResponse(
            success=False,
            message=f"피드백 저장 실패: {str(e)}",
            session_id=request.session_id
        )


@router.post("/company/generate-final", response_model=FinalTextGenerationResponse)
async def generate_final_integrated_text(
    request: FinalTextGenerationRequest,
    agent: Annotated[object, Depends(get_enterprise_quality_agent)]
) -> FinalTextGenerationResponse:
    """
    사용자 선택 기반 최종 통합본 생성 (AI 기반)
    
    테스트 케이스:
    - FS-007 High: 제안 선택 → 200 + 반영된 최종본 + 적용 개수
    - FS-007 Basic: 제안 선택 없음 → 200 + 원본 반환 + 적용 개수 0
    """
    try:
        logger.info(
            f"최종 통합본 생성 시작 - 선택된 제안: "
            f"문법 {len(request.selected_grammar_ids)}개, "
            f"프로토콜 {len(request.selected_protocol_ids)}개"
        )
        
        # 선택된 제안들을 rewrite_service가 요구하는 FeedbackItem 형식으로 변환
        feedback_items = []
        for sugg in request.grammar_suggestions:
            if sugg.id in request.selected_grammar_ids:
                feedback_items.append(
                    FeedbackItem(
                        id=sugg.id,
                        type="grammar",
                        before=sugg.original,
                        after=sugg.suggestion
                    )
                )
        
        for sugg in request.protocol_suggestions:
            if sugg.id in request.selected_protocol_ids:
                feedback_items.append(
                    FeedbackItem(
                        id=sugg.id,
                        type="protocol",
                        before=sugg.original,
                        after=sugg.suggestion
                    )
                )

        if not feedback_items:
            return FinalTextGenerationResponse(
                success=True,
                finalText=request.original_text,
                appliedSuggestions={
                    'grammarCount': 0,
                    'protocolCount': 0,
                    'totalApplied': 0
                },
                originalLength=len(request.original_text),
                finalLength=len(request.original_text),
                message="적용할 제안이 선택되지 않았습니다."
            )

        rewrite_result = rewrite_text(
            text=request.original_text,
            traits={},
            feedback=[fb.model_dump() for fb in feedback_items],
            options={"strict_policy": True}
        )

        final_text = rewrite_result.get("revised_text", request.original_text)
        
        return FinalTextGenerationResponse(
            success=True,
            finalText=final_text,
            appliedSuggestions={
                'grammarCount': len([fb for fb in feedback_items if fb.type == 'grammar']),
                'protocolCount': len([fb for fb in feedback_items if fb.type == 'protocol']),
                'totalApplied': len(feedback_items)
            },
            originalLength=len(request.original_text),
            finalLength=len(final_text),
            message="AI 기반 최종 통합본이 성공적으로 생성되었습니다."
        )
        
    except Exception as e:
        logger.error(f"최종 통합본 생성 중 오류: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"최종 통합본 생성 중 서버 오류 발생: {e}"
        )


@router.get("/company/{company_id}/status")
async def get_company_setup_status(
    company_id: str,
    db_service: Annotated[object, Depends(get_enterprise_db_service_dep)]
) -> Dict[str, Any]:
    """기업 설정 상태 확인"""
    try:
        # DB에서 기업 정보 조회
        profile = await db_service.get_company_profile(company_id)
        guidelines = await db_service.get_company_guidelines(company_id)
        
        profile_exists = profile is not None
        guidelines_count = len(guidelines) if guidelines else 0
        
        # 상태 결정
        if profile_exists and guidelines_count > 0:
            status = "ready"
        elif profile_exists:
            status = "incomplete"
        else:
            status = "not_found"
        
        return {
            "company_id": company_id,
            "status": status,
            "profile_exists": profile_exists,
            "guidelines_count": guidelines_count,
            "company_name": profile.get('company_name') if profile else None,
            "communication_style": profile.get('communication_style') if profile else None,
            "ready_for_analysis": status == "ready"
        }
        
    except Exception as e:
        logger.error(f"기업 상태 확인 중 오류: {e}")
        return {
            "company_id": company_id,
            "status": "error",
            "error": str(e),
            "ready_for_analysis": False
        }


@router.post("/company/test-setup")
async def create_test_company_setup(
    company_id: str,
    db_service: Annotated[EnterpriseDBService, Depends(get_enterprise_db_service_dep)]
) -> Dict[str, Any]:
    """테스트용 기업 설정 생성 (개발/테스트용)"""
    try:
        # 테스트 회사 데이터 생성
        success = await db_service.create_test_company(company_id)
        
        if success:
            # 상태 확인
            profile = await db_service.get_company_profile(company_id)
            guidelines = await db_service.get_company_guidelines(company_id)
            
            return {
                "success": True,
                "message": f"테스트 기업 '{company_id}' 설정이 생성되었습니다",
                "company_id": company_id,
                "status": {
                    "profile_exists": profile is not None,
                    "guidelines_count": len(guidelines) if guidelines else 0,
                    "ready_for_analysis": True
                }
            }
        else:
            return {
                "success": False,
                "message": "테스트 기업 설정 생성에 실패했습니다",
                "error": "DB 작업 실패"
            }
            
    except Exception as e:
        logger.error(f"테스트 설정 생성 중 오류: {e}")
        return {
            "success": False,
            "message": "테스트 설정 생성 중 오류가 발생했습니다",
            "error": str(e)
        }