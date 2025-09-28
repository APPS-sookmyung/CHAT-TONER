"""
Text Quality Analysis Endpoints (기업용 확장) - 수정된 버전
Agent를 직접 사용하여 서비스 중복 제거
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
import json
import logging
from typing import Annotated, Dict, Any

# 수정된 imports - 존재하는 모듈들만 import
from services.rag_service import RAGService 
from services.enterprise_db_service import get_enterprise_db_service, EnterpriseDBService
from agents.quality_analysis_agent import OptimizedEnterpriseQualityAgent
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

logger = logging.getLogger('chattoner')
router = APIRouter()

def get_rag_service():
    """RAG 서비스 인스턴스 생성"""
    try:
        return RAGService()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"RAG 서비스를 사용할 수 없습니다: {str(e)}")

# Agent 직접 생성 의존성
async def get_enterprise_quality_agent(
    rag_service: Annotated[RAGService, Depends(get_rag_service)],
    db_service: Annotated[EnterpriseDBService, Depends(get_enterprise_db_service)]
) -> OptimizedEnterpriseQualityAgent:
    """기업용 품질분석 Agent 인스턴스 생성"""
    try:
        return OptimizedEnterpriseQualityAgent(rag_service, db_service)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"기업용 품질분석 Agent를 생성할 수 없습니다: {str(e)}")

@router.get("/company/options", response_model=DropdownOptions)
async def get_dropdown_options() -> DropdownOptions:
    """프론트엔드 드롭다운 옵션 제공"""
    return DropdownOptions()

@router.post("/company/analyze", response_model=CompanyQualityAnalysisResponse)
async def analyze_company_text_quality(
    request: CompanyQualityAnalysisRequest,
    agent: Annotated[OptimizedEnterpriseQualityAgent, Depends(get_enterprise_quality_agent)]
) -> CompanyQualityAnalysisResponse:
    """기업용 텍스트 품질 분석 (문법 + 프로토콜 분석)"""
    
    try:
        logger.info(f"기업용 품질분석 시작 - 회사: {request.company_id}, 대상: {request.target_audience.value}, 상황: {request.context.value}")
        
        # Agent 직접 호출
        result = await agent.analyze_enterprise_quality(
            text=request.text,
            target_audience=request.target_audience.value,
            context=request.context.value,
            company_id=request.company_id,
            user_id=request.user_id
        )
        
        if result.get('error'):
            logger.warning(f"기업용 분석 중 경고: {result['error']}")
        
        # Agent 결과를 API 응답 형식으로 변환
        response = CompanyQualityAnalysisResponse(
            # 기본 점수들
            grammarScore=result.get('grammar_score', 60.0),
            formalityScore=result.get('formality_score', 60.0), 
            readabilityScore=result.get('readability_score', 60.0),
            protocolScore=result.get('protocol_score', 60.0),
            complianceScore=result.get('compliance_score', 60.0),
            
            # 섹션별 결과
            grammarSection=GrammarSection(
                score=result.get('grammar_score', 60.0),
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
                score=result.get('protocol_score', 60.0),
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
                complianceLevel=result.get('compliance_score', 60.0),
                methodUsed=result.get('optimization_info', {}).get('analysis_method', 'comprehensive'),
                processingTime=result.get('processing_time', 0.0),
                ragSourcesCount=result.get('rag_sources_count', 0)
            )
        )
        
        logger.info(f"기업용 분석 완료 - 소요시간: {result.get('processing_time', 0):.2f}초")
        return response
        
    except Exception as e:
        logger.error(f"기업용 품질분석 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"기업용 품질분석 실패: {str(e)}")

@router.post("/company/feedback", response_model=UserFeedbackResponse)
async def save_user_feedback(
    request: UserFeedbackRequest,
    background_tasks: BackgroundTasks,
    db_service: Annotated[EnterpriseDBService, Depends(get_enterprise_db_service)]
) -> UserFeedbackResponse:
    """사용자 피드백 저장 (good/bad 선택)"""
    
    try:
        logger.info(f"사용자 피드백 저장 - 세션: {request.session_id}, 타입: {request.feedback_type.value}")
        
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
    agent: Annotated[OptimizedEnterpriseQualityAgent, Depends(get_enterprise_quality_agent)]
) -> FinalTextGenerationResponse:
    """사용자 선택 기반 최종 통합본 생성"""
    
    try:
        logger.info(f"최종 통합본 생성 - 선택된 제안: 문법 {len(request.selected_grammar_ids)}개, 프로토콜 {len(request.selected_protocol_ids)}개")
        
        # 선택된 제안들 필터링
        selected_grammar_suggestions = [
            {
                'id': sugg.id,
                'original': sugg.original,
                'suggestion': sugg.suggestion,
                'reason': sugg.reason
            }
            for sugg in request.grammar_suggestions 
            if sugg.id in request.selected_grammar_ids
        ]
        
        selected_protocol_suggestions = [
            {
                'id': sugg.id,
                'original': sugg.original,
                'suggestion': sugg.suggestion,
                'reason': sugg.reason
            }
            for sugg in request.protocol_suggestions 
            if sugg.id in request.selected_protocol_ids
        ]
        
        # RAG를 통한 최종 통합본 생성 (간단한 구현)
        try:
            # 실제로는 Agent나 RAG 서비스를 통해 더 정교하게 구현
            final_text = request.original_text
            
            # 문법 제안 적용 (간단한 문자열 치환)
            for sugg in selected_grammar_suggestions:
                if sugg['original'] in final_text:
                    final_text = final_text.replace(sugg['original'], sugg['suggestion'])
            
            # 프로토콜 제안 적용
            for sugg in selected_protocol_suggestions:
                if sugg['original'] in final_text:
                    final_text = final_text.replace(sugg['original'], sugg['suggestion'])
            
            return FinalTextGenerationResponse(
                success=True,
                finalText=final_text,
                appliedSuggestions={
                    'grammarCount': len(selected_grammar_suggestions),
                    'protocolCount': len(selected_protocol_suggestions),
                    'totalApplied': len(selected_grammar_suggestions) + len(selected_protocol_suggestions)
                },
                originalLength=len(request.original_text),
                finalLength=len(final_text),
                message="최종 통합본이 성공적으로 생성되었습니다"
            )
            
        except Exception as e:
            logger.error(f"통합본 생성 로직 오류: {e}")
            raise
        
    except Exception as e:
        logger.error(f"최종 통합본 생성 중 오류: {e}")
        return FinalTextGenerationResponse(
            success=False,
            finalText=request.original_text,
            appliedSuggestions={'grammarCount': 0, 'protocolCount': 0, 'totalApplied': 0},
            originalLength=len(request.original_text),
            finalLength=len(request.original_text),
            message=f"통합본 생성 실패: {str(e)}"
        )

@router.get("/company/{company_id}/status")
async def get_company_setup_status(
    company_id: str,
    db_service: Annotated[EnterpriseDBService, Depends(get_enterprise_db_service)]
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
    company_id: str = "test_company",
    db_service: Annotated[EnterpriseDBService, Depends(get_enterprise_db_service)] = None
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