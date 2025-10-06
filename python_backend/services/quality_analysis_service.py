"""
기업용 품질분석 서비스 - Service Layer
Agent 우선 실행, 실패 시 Emergency Fallback
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from .rag_service import RAGService
from services.rewrite_service import rewrite_text

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
    enable_llm_in_emergency: bool = True
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
                # DB가 없으면 Agent도 초기화할 수 없으므로 여기서 중단
                return

        # Agent 초기화 (DB 서비스가 성공적으로 초기화된 경우)
        if self.enterprise_agent is None:
            try:
                from agents.quality_analysis_agent import (
                    OptimizedEnterpriseQualityAgent,
                    OptimizedEnterpriseQualityConfig
                )
                
                # 유효한 파라미터만 사용하여 Agent 설정 객체 생성
                agent_config = OptimizedEnterpriseQualityConfig(
                    enable_llm_fallback=self.config.enable_llm_in_emergency
                )
                
                self.enterprise_agent = OptimizedEnterpriseQualityAgent(
                    self.rag_service, 
                    self.db_service, 
                    agent_config
                )
                
                logger.info("기업용 Agent 초기화 완료")
                
            except Exception as e:
                logger.warning(f"Agent 초기화 실패: {e}")
                # Agent 초기화에 실패해도 서비스는 계속 동작해야 함
    
    async def analyze_enterprise_text(
        self,
        text: str,
        target_audience: str,
        context: str,
        company_id: str,
        user_id: str,
        detailed: bool = False
    ) -> Dict[str, Any]:
        """기업용 텍스트 품질 분석 (Agent 우선, Emergency fallback)"""
        
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
                    
                    # Agent 성공
                    if not result.get('error'):
                        result['processing_time'] = time.time() - start_time
                        result['method_used'] = result.get('optimization_info', {}).get('analysis_method', 'agent')
                        
                        if detailed:
                            result.update(await self._add_enterprise_detailed_analysis(
                                result, text, target_audience, context
                            ))
                        
                        logger.info(f"Agent 분석 완료 - 방법: {result['method_used']}")
                        return result
                    
                    # Agent가 에러 반환 → Emergency로
                    logger.warning(f"Agent 분석 실패: {result.get('error')} - Emergency 모드로 전환")
                    
                except Exception as e:
                    # Agent 실행 중 예외 → Emergency로
                    logger.error(f"Agent 실행 중 예외: {e} - Emergency 모드로 전환")
            
            else:
                # Agent 없음 → Emergency로
                logger.warning("Agent 초기화 실패 - Emergency 분석 실행")
            
            # Emergency Analysis 실행
            return await self._emergency_analysis(
                text, target_audience, context, company_id, start_time
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
                return await self._emergency_analysis(
                    text, target_audience, context, company_id, start_time,
                    error_msg=str(e)
                )
            else:
                return self._create_error_response(
                    text, target_audience, context, str(e), start_time
                )
    
    async def _emergency_analysis(
        self,
        text: str,
        target_audience: str,
        context: str,
        company_id: str,
        start_time: float,
        error_msg: str = "Agent 비활성화"
    ) -> Dict[str, Any]:
        """Emergency 분석: 규칙 기반 + 경량 LLM 제안"""
        
        logger.warning(f"Emergency 분석 시작 (이유: {error_msg})")
        
        # 1단계: rewrite_text로 분석
        result = rewrite_text(
            text=text,
            traits={},
            context={
                "audience": self._map_target_to_audience(target_audience),
                "channel": self._map_context_to_channel(context)
            },
            options={"analysis_only": True}
        )
        
        # 2단계: 기본 점수 계산
        scores = self._calculate_basic_scores(result)
        
        # 3단계: LLM으로 제안 생성 (설정 활성화 시)
        if self.config.enable_llm_in_emergency:
            suggestions = await self._generate_emergency_suggestions_with_llm(
                text, result, target_audience, context
            )
        else:
            suggestions = self._create_basic_suggestions(result)
        
        processing_time = time.time() - start_time
        
        return {
            **scores,
            "compliance_score": (scores["protocol_score"] + scores["formality_score"]) / 2,
            "suggestions": suggestions["grammar"],
            "protocol_suggestions": suggestions["protocol"],
            "grammar_section": {
                "score": scores["grammar_score"],
                "suggestions": suggestions["grammar"]
            },
            "protocol_section": {
                "score": scores["protocol_score"],
                "suggestions": suggestions["protocol"]
            },
            "company_analysis": {
                "company_id": company_id,
                "communication_style": "unknown",
                "compliance_level": scores["protocol_score"]
            },
            "processing_time": processing_time,
            "method_used": "emergency_with_llm" if self.config.enable_llm_in_emergency else "emergency_basic",
            "warnings": [f"Emergency 분석 모드: {error_msg}"]
        }
    
    def _calculate_basic_scores(self, rewrite_result: dict, company_profile: dict = None) -> dict:
        """기본 점수 계산 (company_profile 있으면 Agent와 동일한 조정 적용)"""
        
        grammar = rewrite_result.get("grammar", {})
        protocol = rewrite_result.get("protocol", {})
        
        # 1) 절대 평가 점수 계산
        base_grammar = grammar.get("metrics", {}).get("grammar_score", 70.0)
        base_formality = self._extract_formality_score(grammar)
        base_readability = self._extract_readability_score(grammar)
        base_protocol = protocol.get("metrics", {}).get("policy_score", 0.7) * 100
        
        # 2) company_profile이 없으면 절대 평가만 반환
        if not company_profile:
            return {
                "grammar_score": base_grammar,
                "formality_score": base_formality,
                "readability_score": base_readability,
                "protocol_score": base_protocol
            }
        
        # 3) company_profile이 있으면 Agent와 동일한 Expectation-Gap 적용
        company_style = company_profile.get("communication_style", "formal")
        expectations = {
            "strict": {"formality": 90, "protocol": 85},
            "formal": {"formality": 80, "protocol": 75},
            "friendly": {"formality": 70, "protocol": 65}
        }
        expected = expectations.get(company_style, expectations["formal"])
        
        # Gap 계산 및 페널티 적용 (Agent와 동일)
        formality_gap = max(0, expected["formality"] - base_formality)
        protocol_gap = max(0, expected["protocol"] - base_protocol)
        
        formality_penalty = formality_gap * 0.2
        protocol_penalty = protocol_gap * 0.3
        
        adjusted_formality = max(0, base_formality - formality_penalty)
        adjusted_protocol = max(0, base_protocol - protocol_penalty)
        
        return {
            "grammar_score": base_grammar,
            "formality_score": adjusted_formality,  # 조정됨
            "readability_score": base_readability,
            "protocol_score": adjusted_protocol     # 조정됨
        }
    
    def _extract_formality_score(self, grammar: dict) -> float:
        """격식도 점수 추출"""
        korean_endings = grammar.get("korean_endings", {})
        if korean_endings.get("ending_ok"):
            return 85.0
        
        speech_map = {
            "합쇼체": 80.0,
            "해요체": 75.0,
            "의문형": 78.0,
            "평서/반말": 60.0
        }
        return speech_map.get(korean_endings.get("speech_level"), 65.0)
    
    def _extract_readability_score(self, grammar: dict) -> float:
        """가독성 점수 추출"""
        avg_len = grammar.get("metrics", {}).get("avg_sentence_len", 30)
        if avg_len < 20: return 90.0
        if avg_len < 30: return 85.0
        if avg_len < 50: return 75.0
        if avg_len < 80: return 65.0
        return 55.0
    
    async def _generate_emergency_suggestions_with_llm(
        self,
        text: str,
        analysis_result: dict,
        target_audience: str,
        context: str
    ) -> dict:
        """Emergency 상황에서 경량 LLM으로 제안 생성"""
        
        grammar = analysis_result.get("grammar", {})
        protocol = analysis_result.get("protocol", {})
        
        # 문제점 요약
        issues = []
        korean_endings = grammar.get("korean_endings", {})
        if not korean_endings.get("ending_ok"):
            issues.append(f"- 어미: {korean_endings.get('speech_level', '부적절')}")
        
        banned = protocol.get("flags", {}).get("banned_terms", [])
        if banned:
            issues.append(f"- 금칙어: {', '.join(banned[:2])}")
        
        missing = protocol.get("details", {}).get("missing_sections", [])
        if missing:
            issues.append(f"- 누락: {', '.join(missing[:2])}")
        
        issues_summary = "\n".join(issues) if issues else "주요 문제 없음"
        
        # 초경량 프롬프트
        prompt = f"""텍스트 개선 제안을 생성하세요.

원문: {text[:200]}...
대상: {target_audience}
상황: {context}

문제점:
{issues_summary}

JSON 형식:
{{
    "grammar": [{{"original": "문제 표현", "suggestion": "개선", "reason": "이유"}}],
    "protocol": [{{"violation": "위반", "correction": "수정", "severity": "medium"}}]
}}

최대 3개씩만."""
        
        try:
            result = await self.rag_service.ask_generative_question(
                query=prompt,
                context="Emergency 제안 생성"
            )
            
            if result and result.get("success"):
                import json
                suggestions = json.loads(result["answer"])
                
                return {
                    "grammar": [
                        {
                            "category": "문법",
                            "original":
                            s.get("original", ""),
                            "suggestion": s.get("suggestion", ""),
                            "reason": s.get("reason", "")
                        }
                        for s in suggestions.get("grammar", [])[:3]
                    ],
                    "protocol": [
                        {
                            "category": "프로토콜",
                            "rule": "프로토콜",
                            "violation": s.get("violation", ""),
                            "correction": s.get("correction", ""),
                            "severity": s.get("severity", "medium")
                        }
                        for s in suggestions.get("protocol", [])[:3]
                    ]
                }
        except Exception as e:
            logger.error(f"Emergency LLM 제안 실패: {e}")
        
        # LLM 실패 시 기본 제안
        return self._create_basic_suggestions(analysis_result)
    
    def _create_basic_suggestions(self, analysis_result: dict) -> dict:
        """기본 제안 (LLM 없이)"""
        protocol = analysis_result.get("protocol", {})
        
        suggestions = {
            "grammar": [],
            "protocol": []
        }
        
        # 금칙어만 구체적
        banned = protocol.get("flags", {}).get("banned_terms", [])
        for term in banned[:2]:
            suggestions["protocol"].append({
                "category": "프로토콜",
                "rule": "금칙어",
                "violation": term,
                "correction": "대체 표현 사용",
                "severity": "high"
            })
        
        # 섹션 누락
        missing = protocol.get("details", {}).get("missing_sections", [])
        for section in missing[:1]:
            suggestions["protocol"].append({
                "category": "프로토콜",
                "rule": "필수 섹션",
                "violation": f"{section} 누락",
                "correction": f"{section} 추가 권장",
                "severity": "medium"
            })
        
        return suggestions
    
    def _map_target_to_audience(self, target_audience: str) -> List[str]:
        """대상 매핑"""
        mapping = {
            "직속상사": ["executives"],
            "팀동료": ["team"],
            "타부서담당자": ["team"],
            "클라이언트": ["clients_vendors"],
            "외부협력업체": ["clients_vendors"],
            "후배신입": ["team"]
        }
        return mapping.get(target_audience, ["team"])
    
    def _map_context_to_channel(self, context: str) -> str:
        """상황 매핑"""
        mapping = {
            "보고서": "report",
            "회의록": "meeting_minutes",
            "이메일": "email",
            "공지사항": "email",
            "메시지": "chat"
        }
        return mapping.get(context, "email")
    
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
                'improvement_priority': self._determine_enterprise_improvement_priority(base_result)
            }
        }
        
        return detailed_info
    
    def _determine_enterprise_improvement_priority(self, result: Dict[str, Any]) -> List[str]:
        """개선 우선순위 결정"""
        priorities = []
        
        if result.get('protocol_score', 70) < 70:
            priorities.append("기업 프로토콜 준수")
        if result.get('formality_score', 70) < 70:
            priorities.append("격식도 조정")
        if result.get('grammar_score', 70) < 70:
            priorities.append("문법 개선")
        if result.get('readability_score', 70) < 70:
            priorities.append("가독성 향상")
        
        return priorities or ["전반적 품질 향상"]
    
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