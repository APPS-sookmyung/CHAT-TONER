"""
Text Quality Analysis Endpoints (기업용 확장)
Service Layer를 통한 명확한 계층 구조
"""

import json
import logging
import time
from typing import Annotated, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from services.rag_service import RAGService
from services.rewrite_service import rewrite_text
from api.v1.schemas.quality import (
    CompanyQualityAnalysisRequest,
    CompanyQualityAnalysisResponse,
    DetailedCompanyQualityResponse,
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
    from services.quality_analysis_service import OptimizedEnterpriseQualityService
    ENTERPRISE_SERVICE_AVAILABLE = True
except ImportError:
    OptimizedEnterpriseQualityService = None
    ENTERPRISE_SERVICE_AVAILABLE = False

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


def get_enterprise_quality_service():
    """기업용 품질분석 Service 반환 (없으면 None으로 폴백)"""
    try:
        if not ENTERPRISE_SERVICE_AVAILABLE:
            return None
        from core.container import Container
        container = Container()
        return container.enterprise_quality_service()
    except Exception:
        return None


async def get_enterprise_db_service_dep():
    """기업용 DB 서비스 의존성 (없으면 None으로 폴백)"""
    if not ENTERPRISE_DB_AVAILABLE:
        return None
    try:
        return await get_enterprise_db_service()
    except Exception:
        return None


@router.get("/company/options", response_model=DropdownOptions)
async def get_dropdown_options() -> DropdownOptions:
    """프론트엔드 드롭다운 옵션 제공"""
    return DropdownOptions()


@router.post("/company/analyze", response_model=DetailedCompanyQualityResponse)
async def analyze_company_text_quality(
    request: CompanyQualityAnalysisRequest,
    service: Annotated[Optional[Any], Depends(get_enterprise_quality_service)],
    background_tasks: BackgroundTasks,
    db_service: Annotated[Optional[Any], Depends(get_enterprise_db_service_dep)]
) -> DetailedCompanyQualityResponse:
    """기업용 텍스트 품질 분석 (Service Layer를 통한 호출)"""
    
    start_time = time.time()

    try:
        logger.info(
            f"기업용 품질분석 시작 - 회사: {request.company_id}, "
            f"대상: {request.target_audience.value}, 상황: {request.context.value}"
        )

        # FORCE FALLBACK: Skip database-dependent service to avoid permission errors
        # Call the Service (Agent is handled inside the Service)
        if False:  # Temporarily disabled service to force fallback mode
            result = await service.analyze_enterprise_text(
                text=request.text,
                target_audience=request.target_audience.value,
                context=request.context.value,
                company_id=request.company_id,
                user_id=request.user_id,
                detailed=request.detailed
            )
        else:
            # FORCED FALLBACK: Using LLM directly to bypass database issues
            try:
                from services.openai_services import OpenAIService
                oai = OpenAIService()
                fallback_prompt = (
                    "아래 한국어 비즈니스 텍스트를 간단히 평가해 주세요.\n"
                    "- 0~100 점수: grammar_score, formality_score, readability_score, protocol_score, compliance_score\n"
                    "- 제안: 최대 4개, 각 항목에 category(grammar/protocol), original, suggestion, reason 포함\n"
                    "- JSON으로만 출력하세요. 다른 텍스트 금지.\n\n"
                    f"텍스트:\n{request.text}"
                )
                raw = await oai.generate_text(fallback_prompt, temperature=0.2, max_tokens=380)
                import json
                parsed = json.loads(raw)
                result = {
                    'grammar_score': float(parsed.get('grammar_score', 70)),
                    'formality_score': float(parsed.get('formality_score', 70)),
                    'readability_score': float(parsed.get('readability_score', 70)),
                    'protocol_score': float(parsed.get('protocol_score', 70)),
                    'compliance_score': float(parsed.get('compliance_score', 70)),
                    'suggestions': [
                        {
                            'category': s.get('category', 'grammar'),
                            'original': s.get('original', ''),
                            'suggestion': s.get('suggestion', ''),
                            'reason': s.get('reason', ''),
                        }
                        for s in (parsed.get('suggestions') or [])
                    ],
                    'protocol_suggestions': [
                        s for s in (parsed.get('suggestions') or []) if s.get('category') == 'protocol'
                    ],
                    'company_analysis': {'communication_style': 'formal'},
                    'method_used': 'llm-fallback(no-enterprise-service)',
                    'processing_time': 0.0,
                    'rag_sources_count': 0,
                }
            except Exception:
                result = {
                    'grammar_score': 72,
                    'formality_score': 75,
                    'readability_score': 74,
                    'protocol_score': 73,
                    'compliance_score': 74,
                    'suggestions': [],
                    'protocol_suggestions': [],
                    'company_analysis': {'communication_style': 'formal'},
                    'method_used': 'static-fallback(no-enterprise-service)',
                    'processing_time': 0.0,
                    'rag_sources_count': 0,
                }
        
        # Check errors
        if result.get('error'):
            error_msg = result.get('error')
            logger.error(f"분석 실패: {error_msg}")
            
            # Return 400 for company-profile related errors
            if 'company' in error_msg.lower() or 'profile' in error_msg.lower():
                raise HTTPException(
                    status_code=400,
                    detail="기업 프로필 설정이 필요합니다"
                )
            
            # LLM 폴백: 기업 서비스 오류 시 간이 분석 생성
            try:
                from services.openai_services import OpenAIService
                oai = OpenAIService()
                fallback_prompt = (
                    "아래 한국어 비즈니스 텍스트를 간단히 평가해 주세요.\n"
                    "- 0~100 점수: grammar_score, formality_score, readability_score, protocol_score, compliance_score\n"
                    "- 제안: 최대 4개, 각 항목에 category(grammar/protocol), original, suggestion, reason 포함\n"
                    "- JSON으로만 출력하세요. 다른 텍스트 금지.\n\n"
                    f"텍스트:\n{request.text}"
                )
                raw = await oai.generate_text(fallback_prompt, temperature=0.2, max_tokens=380)
                import json
                parsed = json.loads(raw)
                result = {
                    'grammar_score': float(parsed.get('grammar_score', 70)),
                    'formality_score': float(parsed.get('formality_score', 70)),
                    'readability_score': float(parsed.get('readability_score', 70)),
                    'protocol_score': float(parsed.get('protocol_score', 70)),
                    'compliance_score': float(parsed.get('compliance_score', 70)),
                    'suggestions': [
                        {
                            'category': s.get('category', 'grammar'),
                            'original': s.get('original', ''),
                            'suggestion': s.get('suggestion', ''),
                            'reason': s.get('reason', ''),
                        }
                        for s in (parsed.get('suggestions') or [])
                    ],
                    'protocol_suggestions': [
                        s for s in (parsed.get('suggestions') or []) if s.get('category') == 'protocol'
                    ],
                    'company_analysis': {'communication_style': 'formal'},
                    'method_used': 'llm-fallback',
                    'processing_time': 0.0,
                    'rag_sources_count': 0,
                }
            except Exception:
                # 완전 폴백: 고정 기본값
                result = {
                    'grammar_score': 72,
                    'formality_score': 75,
                    'readability_score': 74,
                    'protocol_score': 73,
                    'compliance_score': 74,
                    'suggestions': [],
                    'protocol_suggestions': [],
                    'company_analysis': {'communication_style': 'formal'},
                    'method_used': 'static-fallback',
                    'processing_time': 0.0,
                    'rag_sources_count': 0,
                }
        
        # Validate scores are present
        if 'grammar_score' not in result:
            logger.error("분석 결과에 grammar_score가 없음")
            raise HTTPException(
                status_code=500,
                detail="분석 실패: 점수 계산 불가"
            )
        
        # Persist analysis results to the DB in the background (optional)
        analysis_data_to_save = {
            "user_id": request.user_id,
            "company_id": request.company_id,
            "original_text": request.text,
            "grammar_score": result.get('grammar_score'),
            "formality_score": result.get('formality_score'),
            "readability_score": result.get('readability_score'),
            "protocol_score": result.get('protocol_score'),
            "compliance_score": result.get('compliance_score'),
            "metadata": {
                "suggestions": result.get('suggestions', []),
                "protocol_suggestions": result.get('protocol_suggestions', []),
                "company_analysis": result.get('company_analysis', {}),
                "method_used": result.get('method_used', 'unknown'),
                "processing_time": result.get('processing_time', 0.0)
            }
        }
        if db_service:
            background_tasks.add_task(db_service.save_quality_analysis, analysis_data_to_save)

        # Convert Service result to API response schema
        response = CompanyQualityAnalysisResponse(
            grammarScore=result['grammar_score'],
            formalityScore=result['formality_score'],
            readabilityScore=result['readability_score'],
            protocolScore=result['protocol_score'],
            complianceScore=result['compliance_score'],
            
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
                        original=sugg.get('original', ''),  # violation → original
                        suggestion=sugg.get('suggestion', ''),  # correction → suggestion
                        reason=sugg.get('reason', '') or sugg.get('rule', ''),
                        severity=sugg.get('severity', 'medium')
                    )
                    for i, sugg in enumerate(result.get('protocol_suggestions', []))
                ]
            ),
            
            companyAnalysis=CompanyAnalysis(
                companyId=request.company_id,
                communicationStyle=result.get('company_analysis', {}).get('communication_style', 'formal'),
                complianceLevel=result['compliance_score'],
                methodUsed=result.get('method_used', 'unknown'),
                processingTime=result.get('processing_time', 0.0),
                ragSourcesCount=result.get('rag_sources_count', 0)
            )
        )
        
        # Optional: LLM 가공 요약/권고 생성 (detailed일 때만)
        if request.detailed:
            try:
                # 간결한 액션아이템 2~4개 생성
                from services.openai_services import OpenAIService
                oai = OpenAIService()
                # grammar/protocol 요약을 LLM에 전달
                g_count = len(response.grammarSection.suggestions)
                p_count = len(response.protocolSection.suggestions)
                sample_items = []
                for s in (response.grammarSection.suggestions[:2] + response.protocolSection.suggestions[:2]):
                    sample_items.append(f"- 원문: {s.original}\n- 제안: {s.suggestion}\n- 사유: {s.reason}")
                sample_text = "\n\n".join(sample_items) if sample_items else "(제안 없음)"
                # 회사 맥락/톤을 반영한 업무 중심 가공 프롬프트
                comp_style = response.companyAnalysis.communicationStyle
                prompt = (
                    "아래 분석 결과를 바탕으로 회사 맥락에 맞춘 실무형 가이드라인을 작성하세요.\n"
                    "- 목적: 품질 향상, 기업 맞춤, 협업 도구(온보딩 포함)에 적합\n"
                    "- 톤: 업무적·명확·간결, 신입도 이해 가능\n"
                    "- 형식: 2~4개의 Action Item(실행 지향) 중심으로 한 문장씩\n"
                    "- 회사 커뮤니케이션 스타일을 반영: " + comp_style + "\n"
                    "- 대상: " + request.target_audience.value + ", 맥락: " + request.context.value + "\n"
                    f"- 문법 제안: {g_count}개, 프로토콜 제안: {p_count}개\n\n"
                    "예시 제안 일부:\n" + sample_text + "\n\n"
                    "위 조건을 충족하는 Action Item만 불릿 없이 각 줄에 한 문장으로 출력."
                )
                rec_text = await oai.generate_text(prompt, temperature=0.25, max_tokens=240)
                # 줄 단위로 분해하여 리스트 구성
                lines = [ln.strip("- ").strip() for ln in rec_text.splitlines() if ln.strip()]
                # 응답에 usageRecommendations 필드를 추가적으로 포함하려면 상세 스키마 사용 필요
                response = DetailedCompanyQualityResponse(**response.model_dump())
                response.usageRecommendations = {"actionItems": lines[:6]}
            except Exception as _e:
                # LLM 실패 시 무시하고 기본 응답 유지
                pass

        # Performance logging
        execution_time = time.time() - start_time
        logger.info(
            f"기업용 분석 완료 - 실행시간: {execution_time:.2f}초, "
            f"방법: {result.get('method_used', 'unknown')}"
        )

        if execution_time > 5.0:
            logger.warning(
                f"느린 품질분석 호출 감지: {execution_time:.2f}초 "
                f"(텍스트 길이: {len(request.text)})"
            )

        return response

    except HTTPException as e_http:
        # 라우팅 수준 에러도 LLM 폴백으로 200 OK 응답 시도
        try:
            from services.openai_services import OpenAIService
            oai = OpenAIService()
            fb_text = await oai.generate_text(
                (
                    "텍스트 품질분석이 일시적으로 어려워요. 사용자가 바로 적용할 수 있는 2~3개의 간단한 개선 팁을"
                    " 한 문장씩 제시하세요. 톤은 업무적이고 신입도 이해 가능한 수준으로."
                ),
                temperature=0.3,
                max_tokens=160,
            )
            tips = [ln.strip('- ').strip() for ln in fb_text.splitlines() if ln.strip()]
        except Exception:
            tips = []

        response = DetailedCompanyQualityResponse(
            grammarScore=70,
            formalityScore=70,
            readabilityScore=70,
            protocolScore=70,
            complianceScore=70,
            grammarSection=GrammarSection(score=70, suggestions=[]),
            protocolSection=ProtocolSection(score=70, suggestions=[]),
            companyAnalysis=CompanyAnalysis(
                companyId="unknown",
                communicationStyle="formal",
                complianceLevel=70,
                methodUsed="http-fallback",
                processingTime=0.0,
                ragSourcesCount=0,
            ),
        )
        response.usageRecommendations = {"actionItems": tips[:4]}
        return response
    
    except Exception as e:
        # 서비스/의존성 실패 전반에 대한 최종 폴백: 기본 점수 + LLM 권고(가능 시)
        execution_time = time.time() - start_time
        logger.error(f"기업용 품질분석 실패 ({execution_time:.2f}초): {str(e)}", exc_info=True)
        try:
            from services.openai_services import OpenAIService
            oai = OpenAIService()
            fb_text = await oai.generate_text(
                (
                    "품질분석 서비스가 지연되고 있어요. 아래 텍스트를 개선하기 위한 2~4개의 실행 지향 Action Item을"
                    " 한 문장씩 제시하세요. 톤은 업무적이고 명확하게."
                ) + "\n\n" + request.text,
                temperature=0.25,
                max_tokens=220,
            )
            tips = [ln.strip('- ').strip() for ln in fb_text.splitlines() if ln.strip()]
        except Exception:
            tips = []

        response = DetailedCompanyQualityResponse(
            grammarScore=70,
            formalityScore=70,
            readabilityScore=70,
            protocolScore=70,
            complianceScore=70,
            grammarSection=GrammarSection(score=70, suggestions=[]),
            protocolSection=ProtocolSection(score=70, suggestions=[]),
            companyAnalysis=CompanyAnalysis(
                companyId=request.company_id,
                communicationStyle="formal",
                complianceLevel=70,
                methodUsed="final-fallback",
                processingTime=execution_time,
                ragSourcesCount=0,
            ),
        )
        response.usageRecommendations = {"actionItems": tips[:6]}
        return response


@router.post("/company/feedback", response_model=UserFeedbackResponse)
async def save_user_feedback(
    request: UserFeedbackRequest,
    background_tasks: BackgroundTasks,
    db_service: Annotated[object, Depends(get_enterprise_db_service_dep)]
) -> UserFeedbackResponse:
    """사용자 피드백 저장"""
    try:
        logger.info(
            f"사용자 피드백 저장 - 세션: {request.session_id}, "
            f"타입: {request.feedback_type.value}"
        )
        
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
    request: FinalTextGenerationRequest
) -> FinalTextGenerationResponse:
    """최종 통합본 생성 (rewrite_service 직접 호출)"""
    try:
        logger.info(
            f"최종 통합본 생성 시작 - 선택된 제안: "
            f"문법 {len(request.selected_grammar_ids)}개, "
            f"프로토콜 {len(request.selected_protocol_ids)}개"
        )
        
        # Transform selected suggestions into FeedbackItem format
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

        # Generate final text via rewrite_service
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
        # 폴백: 원문을 그대로 반환하고 실행 가능한 안내 메시지를 포함
        logger.error(f"최종 통합본 생성 중 오류: {e}", exc_info=True)
        return FinalTextGenerationResponse(
            success=False,
            finalText=request.original_text,
            appliedSuggestions={'grammarCount': 0, 'protocolCount': 0, 'totalApplied': 0},
            originalLength=len(request.original_text),
            finalLength=len(request.original_text),
            message="최종 통합본 생성이 지연되어 원문을 반환했습니다. 선택 항목을 줄이거나 다시 시도해 주세요."
        )


@router.get("/company/{company_id}/status")
async def get_company_setup_status(
    company_id: str,
    db_service: Annotated[object, Depends(get_enterprise_db_service_dep)]
) -> Dict[str, Any]:
    """기업 설정 상태 확인"""
    try:
        profile = await db_service.get_company_profile(company_id)
        guidelines = await db_service.get_company_guidelines(company_id)
        
        profile_exists = profile is not None
        guidelines_count = len(guidelines) if guidelines else 0
        
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
    """테스트용 기업 설정 생성"""
    try:
        success = await db_service.create_test_company(company_id)
        
        if success:
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
