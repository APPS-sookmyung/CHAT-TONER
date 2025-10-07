"""
기업용 품질분석 서비스 - Service Layer
Agent 우선 실행, Agent 초기화 실패 시에만 Service Fallback
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from .rag_service import RAGService

logger = logging.getLogger('chattoner.quality_analysis_service')

# 정의한 대상/상황 매핑
ENTERPRISE_TARGETS = {
    "직속상사": {"formality_level": "high", "tone": "respectful"},
    "팀동료": {"formality_level": "medium", "tone": "collaborative"},
    "타부서담당자": {"formality_level": "medium-high", "tone": "professional"},
    "클라이언트": {"formality_level": "very-high", "tone": "professional-courteous"},
    "외부협력업체": {"formality_level": "high", "tone": "business-formal"},
    "후배신입": {"formality_level": "medium", "tone": "mentoring"}
}

ENTERPRISE_CONTEXTS = {
    "보고서": {"format_requirements": ["제목", "요약", "세부내용", "결론"]},
    "회의록": {"format_requirements": ["참석자", "안건", "논의내용", "결정사항"]},
    "이메일": {"format_requirements": ["제목", "인사", "본문", "마무리"]},
    "공지사항": {"format_requirements": ["제목", "대상", "내용", "일정"]},
    "메시지": {"format_requirements": ["간결성", "명확성"]}
}


@dataclass
class OptimizedEnterpriseQualityServiceConfig:
    """기업용 품질분석 서비스 설정"""
    enable_enterprise_mode: bool = True
    enable_protocol_analysis: bool = True
    protocol_weight: float = 0.4
    grammar_weight: float = 0.6
    fallback_to_rule_based: bool = True
    enable_llm_in_fallback: bool = True
    db_timeout: float = 30.0


class OptimizedEnterpriseQualityService:
    """기업용 품질분석 서비스 (Agent Orchestrator)"""
    
    def __init__(
        self,
        rag_service: RAGService,
        config: Optional[OptimizedEnterpriseQualityServiceConfig] = None
    ):
        self.rag_service = rag_service
        self.config = config or OptimizedEnterpriseQualityServiceConfig()
        
        # Lazy 초기화
        self.db_service = None
        self.enterprise_agent = None
        
        logger.info("기업용 품질분석 서비스 초기화 완료")
    
    async def _ensure_initialized(self):
        """DB 서비스 및 Agent 초기화 (실패해도 계속)"""
        if self.enterprise_agent is not None:
            return  # 이미 초기화됨

        # DB 서비스 초기화
        if self.db_service is None:
            try:
                from services.enterprise_db_service import get_enterprise_db_service
                self.db_service = await get_enterprise_db_service()
                logger.info("DB 서비스 초기화 완료")
            except Exception as e:
                logger.warning(f"DB 서비스 초기화 실패: {e}")
                return

        # Agent 초기화 (DB 서비스가 성공적으로 초기화된 경우)
        if self.enterprise_agent is None:
            try:
                from agents.quality_analysis_agent import (
                    OptimizedEnterpriseQualityAgent,
                    OptimizedEnterpriseQualityConfig
                )
                
                agent_config = OptimizedEnterpriseQualityConfig(
                    enable_llm_fallback=self.config.enable_llm_in_fallback
                )
                
                self.enterprise_agent = OptimizedEnterpriseQualityAgent(
                    self.rag_service, 
                    self.db_service, 
                    agent_config
                )
                
                logger.info("기업용 Agent 초기화 완료")
                
            except Exception as e:
                logger.warning(f"Agent 초기화 실패: {e}")
    
    async def analyze_enterprise_text(
        self,
        text: str,
        target_audience: str,
        context: str,
        company_id: str,
        user_id: str,
        detailed: bool = False
    ) -> Dict[str, Any]:
        """기업용 텍스트 품질 분석 (Agent 우선, Agent 죽었을 때만 Service Fallback)"""
        
        start_time = time.time()
        
        try:
            # 대상/상황 유효성 검사
            if target_audience not in ENTERPRISE_TARGETS:
                raise ValueError(f"지원하지 않는 대상: {target_audience}")
            
            if context not in ENTERPRISE_CONTEXTS:
                raise ValueError(f"지원하지 않는 상황: {context}")
            
            # 초기화 시도 (실패해도 계속)
            await self._ensure_initialized()
            
            # Agent 있으면 Agent 사용
            if self.enterprise_agent is not None:
                try:
                    logger.info("Agent로 기업용 분석 시작")
                    result = await self.enterprise_agent.analyze_enterprise_quality(
                        text=text,
                        target_audience=target_audience,
                        context=context,
                        company_id=company_id,
                        user_id=user_id
                    )
                    
                    # Agent 성공 (에러 없음)
                    if not result.get('error'):
                        result['processing_time'] = time.time() - start_time
                        result['method_used'] = result.get('optimization_info', {}).get('analysis_method', 'agent')
                        
                        if detailed:
                            result.update(await self._add_enterprise_detailed_analysis(
                                result, text, target_audience, context
                            ))
                        
                        logger.info(f"Agent 분석 완료 - 방법: {result['method_used']}")
                        return result
                    
                    # Agent가 에러 반환 (이론상 발생 안 해야 함)
                    logger.warning(f"Agent 분석 에러: {result.get('error')} - Service Fallback")
                    
                except Exception as e:
                    # Agent 실행 중 예외 (이것도 거의 없어야 함)
                    logger.error(f"Agent 실행 중 예외: {e} - Service Fallback")
            
            else:
                # Agent 초기화 실패 → Service Fallback
                logger.warning("Agent 초기화 실패 - Service Fallback 실행")
            
            # Service Fallback 실행 (Agent가 아예 죽었을 때만)
            return await self._service_fallback_analysis(
                text, target_audience, context, company_id, user_id, start_time
            )
            
        except ValueError as e:
            # 유효성 검사 실패
            logger.error(f"입력 유효성 검사 실패: {e}")
            return self._create_error_response(
                text, target_audience, context, str(e), start_time
            )
        
        except Exception as e:
            # 예외 발생
            logger.error(f"분석 중 예외 발생: {e}")
            
            if self.config.fallback_to_rule_based:
                return await self._service_fallback_analysis(
                    text, target_audience, context, company_id, user_id, start_time,
                    error_msg=str(e)
                )
            else:
                return self._create_error_response(
                    text, target_audience, context, str(e), start_time
                )
    
    async def _service_fallback_analysis(
        self,
        text: str,
        target_audience: str,
        context: str,
        company_id: str,
        user_id: str,
        start_time: float,
        error_msg: str = "Agent 초기화 실패"
    ) -> Dict[str, Any]:
        """
        Service Fallback: Agent가 아예 죽었을 때만 실행
        기업 데이터를 새로 로드해야 함
        """
        from services.rewrite_service import rewrite_text
        from utils.quality_analysis_utils import (
            extract_base_scores,
            apply_expectation_gap,
            map_audience,
            map_channel,
            determine_improvement_priority
        )
        from utils.quality_analysis_llm import generate_suggestions_with_llm
        
        logger.warning(f"Service Fallback 분석 시작 (이유: {error_msg})")
        
        # 1단계: 기업 프로필 로드 (새로 로드해야 함)
        company_profile = None
        if self.db_service:
            try:
                company_profile = await self.db_service.get_company_profile(company_id)
                logger.info(f"기업 프로필 로드 완료: {company_profile.get('communication_style') if company_profile else 'None'}")
            except Exception as e:
                logger.warning(f"기업 프로필 로드 실패: {e}")
        
        # 2단계: rewrite_text로 분석
        rewrite_result = rewrite_text(
            text=text,
            traits={},
            context={
                "audience": map_audience(target_audience),
                "channel": map_channel(context)
            },
            options={"analysis_only": True}
        )
        
        # 3단계: 점수 계산 (기업 맥락 반영)
        base_scores = extract_base_scores(rewrite_result)
        adjusted_scores, adjustment_info = apply_expectation_gap(base_scores, company_profile)
        
        # 4단계: LLM으로 제안 생성 (설정 활성화 시)
        if self.config.enable_llm_in_fallback:
            try:
                suggestions = await generate_suggestions_with_llm(
                    rag_service=self.rag_service,
                    text=text,
                    rewrite_result=rewrite_result,
                    target_audience=target_audience,
                    context=context,
                    company_profile=company_profile,
                    max_grammar=4,
                    max_protocol=4
                )
                method_used = "service_fallback_with_llm"
                logger.info("Service Fallback LLM 제안 생성 완료")
            except Exception as e:
                logger.error(f"LLM 제안 생성 실패: {e}")
                from quality_analysis_utils import create_basic_suggestions
                suggestions = create_basic_suggestions(rewrite_result)
                method_used = "service_fallback_basic"
        else:
            from quality_analysis_utils import create_basic_suggestions
            suggestions = create_basic_suggestions(rewrite_result)
            method_used = "service_fallback_basic"
        
        processing_time = time.time() - start_time
        
        return {
            **adjusted_scores,
            "compliance_score": (adjusted_scores["protocol_score"] + adjusted_scores["formality_score"]) / 2,
            "suggestions": suggestions["grammar"],
            "protocol_suggestions": suggestions["protocol"],
            "grammar_section": {
                "score": adjusted_scores["grammar_score"],
                "suggestions": suggestions["grammar"]
            },
            "protocol_section": {
                "score": adjusted_scores["protocol_score"],
                "suggestions": suggestions["protocol"]
            },
            "company_analysis": {
                "company_id": company_id,
                "communication_style": company_profile.get("communication_style") if company_profile else "unknown",
                "compliance_level": adjusted_scores["protocol_score"],
                "adjustment_applied": adjustment_info.get("adjusted", False)
            },
            "processing_time": processing_time,
            "method_used": method_used,
            "warnings": [f"Service Fallback 모드: {error_msg}"]
        }
    
    def _create_error_response(
        self, 
        text: str, 
        target_audience: str,
        context: str,
        error_msg: str, 
        start_time: float
    ) -> Dict[str, Any]:
        """완전 실패 시 에러 응답"""
        processing_time = time.time() - start_time
        
        return {
            "grammar_score": 0.0,
            "formality_score": 0.0,
            "readability_score": 0.0,
            "protocol_score": 0.0,
            "compliance_score": 0.0,
            "suggestions": [],
            "protocol_suggestions": [],
            "grammar_section": {"score": 0.0, "suggestions": []},
            "protocol_section": {"score": 0.0, "suggestions": []},
            "company_analysis": {
                "company_id": "error",
                "communication_style": "unknown",
                "compliance_level": 0.0
            },
            "processing_time": processing_time,
            "method_used": "system_error",
            "error": error_msg,
            "warnings": ["분석 불가능: 시스템 오류"]
        }
    
    async def _add_enterprise_detailed_analysis(
        self,
        base_result: Dict[str, Any],
        text: str,
        target_audience: str,
        context: str
    ) -> Dict[str, Any]:
        """상세 분석 정보 추가"""
        from quality_analysis_utils import determine_improvement_priority
        
        target_info = ENTERPRISE_TARGETS.get(target_audience, {})
        context_info = ENTERPRISE_CONTEXTS.get(context, {})
        
        detailed_info = {
            'enterprise_analysis': {
                'target_requirements': target_info,
                'context_requirements': context_info,
                'compliance_breakdown': {
                    'target_formality_match': base_result.get('formality_score', 0) >= 70,
                    'context_format_compliance': base_result.get('protocol_score', 0) >= 70,
                    'overall_enterprise_readiness': base_result.get('compliance_score', 0) >= 75
                },
                'improvement_priority': determine_improvement_priority(base_result)
            }
        }
        
        return detailed_info
    
    # 사용자 피드백 처리
    async def save_user_feedback(
        self,
        user_id: str,
        company_id: str,
        session_id: str,
        feedback_data: Dict[str, Any]
    ) -> bool:
        """사용자 피드백 저장"""
        try:
            await self._ensure_initialized()
            
            if self.db_service is None:
                logger.warning("DB 서비스 초기화 실패로 피드백 저장 불가")
                return False
            
            feedback_record = {
                'user_id': user_id,
                'company_id': company_id,
                'session_id': session_id,
                'original_text': feedback_data.get('original_text'),
                'suggested_text': feedback_data.get('suggested_text'),
                'feedback_type': feedback_data.get('feedback_type'),
                'feedback_value': feedback_data.get('feedback_value'),
                'metadata': {
                    'target_audience': feedback_data.get('target_audience'),
                    'context': feedback_data.get('context'),
                    'suggestion_category': feedback_data.get('suggestion_category'),
                    'scores': feedback_data.get('scores', {})
                }
            }
            
            return await self.db_service.save_user_feedback(feedback_record)
            
        except Exception as e:
            logger.error(f"사용자 피드백 저장 실패: {e}")
            return False
    
    # 기업 데이터 관리
    async def get_company_status(self, company_id: str) -> Dict[str, Any]:
        """기업 설정 상태 확인"""
        try:
            await self._ensure_initialized()
            
            if self.db_service is None:
                return {"status": "db_unavailable"}
            
            profile = await self.db_service.get_company_profile(company_id)
            guidelines = await self.db_service.get_company_guidelines(company_id)
            
            return {
                "status": "ready" if profile and guidelines else "incomplete",
                "profile_exists": bool(profile),
                "guidelines_count": len(guidelines),
                "company_name": profile.get('company_name') if profile else None,
                "communication_style": profile.get('communication_style') if profile else None
            }
            
        except Exception as e:
            logger.error(f"기업 상태 확인 실패 ({company_id}): {e}")
            return {"status": "error", "error": str(e)}
    
    async def create_test_setup(self, company_id: str = "test_company") -> Dict[str, Any]:
        """테스트용 기업 설정 생성"""
        try:
            await self._ensure_initialized()
            
            if self.db_service is None:
                return {"success": False, "error": "DB 서비스 초기화 실패"}
            
            success = await self.db_service.create_test_company(company_id)
            
            if success:
                status = await self.get_company_status(company_id)
                return {
                    "success": True,
                    "company_id": company_id,
                    "status": status
                }
            else:
                return {"success": False, "error": "테스트 기업 생성 실패"}
                
        except Exception as e:
            logger.error(f"테스트 설정 생성 실패: {e}")
            return {"success": False, "error": str(e)}