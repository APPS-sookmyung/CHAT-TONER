"""
기업용 품질분석 서비스 - DB 연동 버전
rewrite_text 기반 fallback 적용 (하드코딩 완전 제거)
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

# 기존 imports
from .rag_service import RAGService
from services.rewrite_service import rewrite_text

# 새로운 imports
from agents.quality_analysis_agent import OptimizedEnterpriseQualityAgent, OptimizedEnterpriseQualityConfig 
from .enterprise_db_service import EnterpriseDBService, get_enterprise_db_service

logger = logging.getLogger('chattoner.enterprise_quality_service')

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
    db_timeout: float = 30.0

class OptimizedEnterpriseQualityService:
    """기업용 품질분석 서비스"""
    
    def __init__(
        self,
        rag_service: RAGService,
        config: Optional[OptimizedEnterpriseQualityServiceConfig] = None
    ):
        self.rag_service = rag_service
        self.config = config or OptimizedEnterpriseQualityServiceConfig()
        
        # DB 서비스 (lazy 초기화)
        self.db_service = None
        self.enterprise_agent = None
        
        logger.info("기업용 품질분석 서비스 초기화 완료")
    
    async def _ensure_initialized(self):
        """DB 서비스 및 Agent 초기화"""
        if self.db_service is None:
            try:
                self.db_service = await get_enterprise_db_service()
                
                # Agent 설정
                agent_config = OptimizedEnterpriseQualityConfig(
                    enable_protocol_analysis=self.config.enable_protocol_analysis,
                    protocol_weight=self.config.protocol_weight,
                    grammar_weight=self.config.grammar_weight
                )
                
                self.enterprise_agent = OptimizedEnterpriseQualityAgent(
                    self.rag_service, 
                    self.db_service, 
                    agent_config
                )
                
                logger.info("기업용 Agent 초기화 완료")
                
            except Exception as e:
                logger.error(f"기업용 서비스 초기화 실패: {e}")
                if not self.config.fallback_to_rule_based:
                    raise
    
    async def analyze_enterprise_text(
        self,
        text: str,
        target_audience: str,
        context: str,
        company_id: str,
        user_id: str,
        detailed: bool = False
    ) -> Dict[str, Any]:
        """기업용 텍스트 품질 분석"""
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            # 대상/상황 유효성 검사
            if target_audience not in ENTERPRISE_TARGETS:
                raise ValueError(f"지원하지 않는 대상: {target_audience}")
            
            if context not in ENTERPRISE_CONTEXTS:
                raise ValueError(f"지원하지 않는 상황: {context}")
            
            # 기업용 Agent 초기화
            await self._ensure_initialized()
            
            if self.enterprise_agent is None:
                raise Exception("기업용 Agent 초기화 실패")
            
            # 기업용 분석 실행
            result = await self.enterprise_agent.analyze_enterprise_quality(
                text=text,
                target_audience=target_audience,
                context=context,
                company_id=company_id,
                user_id=user_id
            )
            
            # 처리 시간 추가
            processing_time = asyncio.get_event_loop().time() - start_time
            result['processing_time'] = processing_time
            result['method_used'] = result.get('optimization_info', {}).get('analysis_method', 'enterprise_agent')
            
            # 상세 분석 추가
            if detailed:
                result.update(await self._add_enterprise_detailed_analysis(result, text, target_audience, context))
            
            logger.info(f"기업용 분석 완료 - 소요시간: {processing_time:.2f}초")
            return result
            
        except Exception as e:
            logger.error(f"기업용 분석 실패: {e}")
            
            # Fallback to rule-based analysis
            if self.config.fallback_to_rule_based:
                return await self._fallback_analysis(
                    text, target_audience, context, start_time, str(e)
                )
            else:
                return self._create_error_response(text, target_audience, context, str(e), start_time)
    
    async def _fallback_analysis(
        self,
        text: str,
        target_audience: str,
        context: str,
        start_time: float,
        error_msg: str
    ) -> Dict[str, Any]:
        """규칙 기반 fallback (rewrite_text 활용) - 하드코딩 없음"""
        
        logger.warning(f"규칙 기반 분석으로 전환: {error_msg}")
        
        # 대상/상황을 rewrite_text 형식으로 매핑
        audience_list = self._map_target_to_audience(target_audience)
        channel = self._map_context_to_channel(context)
        
        # rewrite_text로 규칙 기반 분석 실행 (analysis_only=True)
        rewrite_result = rewrite_text(
            text=text,
            traits={},
            context={
                "audience": audience_list,
                "channel": channel,
                "situation": channel
            },
            options={"analysis_only": True}  # 수정 없이 분석만
        )
        
        # rewrite 결과를 기업용 형식으로 변환
        enterprise_result = self._convert_rewrite_to_enterprise_format(
            rewrite_result, 
            target_audience, 
            context
        )
        
        processing_time = asyncio.get_event_loop().time() - start_time
        enterprise_result.update({
            'processing_time': processing_time,
            'method_used': 'rule_based_fallback',
            'fallback_reason': error_msg,
            'fallback_source': 'rewrite_service'
        })
        
        logger.info(f"규칙 기반 fallback 완료: {processing_time:.2f}초")
        return enterprise_result
    
    def _map_target_to_audience(self, target_audience: str) -> List[str]:
        """기업용 대상을 rewrite_text audience로 매핑"""
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
        """기업용 상황을 rewrite_text channel로 매핑"""
        mapping = {
            "보고서": "report",
            "회의록": "meeting_minutes",
            "이메일": "email",
            "공지사항": "email",
            "메시지": "chat"
        }
        return mapping.get(context, "email")
    
    def _convert_rewrite_to_enterprise_format(
        self, 
        rewrite_result: Dict[str, Any],
        target_audience: str,
        context: str
    ) -> Dict[str, Any]:
        """rewrite_text 결과를 기업용 형식으로 변환 (텍스트 기반 점수)"""
        
        grammar = rewrite_result.get("grammar", {})
        protocol = rewrite_result.get("protocol", {})
        
        # 문법 점수 - rewrite_service 계산값 사용
        grammar_score = grammar.get("metrics", {}).get("grammar_score", 70.0)
        
        # 격식도 - 어미 분석 기반
        korean_endings = grammar.get("korean_endings", {})
        if korean_endings.get("ending_ok"):
            formality_score = 85.0
        else:
            speech_level = korean_endings.get("speech_level", "기타")
            formality_map = {
                "합쇼체": 80.0,
                "해요체": 75.0,
                "의문형": 78.0,
                "평서/반말": 60.0,
                "기타": 65.0
            }
            formality_score = formality_map.get(speech_level, 65.0)
        
        # 가독성 - 평균 문장 길이 기반
        avg_len = grammar.get("metrics", {}).get("avg_sentence_len", 30)
        if avg_len < 20:
            readability_score = 90.0
        elif avg_len < 30:
            readability_score = 85.0
        elif avg_len < 50:
            readability_score = 75.0
        elif avg_len < 80:
            readability_score = 65.0
        else:
            readability_score = 55.0
        
        # 프로토콜 점수
        protocol_score = protocol.get("metrics", {}).get("policy_score", 0.7) * 100
        
        # 제안사항 구성 (change_log에서 추출)
        change_log = rewrite_result.get("change_log", {})
        applied_fixes = change_log.get("applied_fixes", [])
        
        grammar_suggestions = []
        protocol_suggestions = []
        
        for fix in applied_fixes[:4]:
            if fix.get("rule") in ["grammar", "clarity"]:
                grammar_suggestions.append({
                    "category": "문법",
                    "original": fix.get("before", ""),
                    "suggestion": fix.get("after", ""),
                    "reason": f"{fix.get('rule')} 개선"
                })
            elif fix.get("rule") == "term":
                grammar_suggestions.append({
                    "category": "용어",
                    "original": fix.get("before", ""),
                    "suggestion": fix.get("after", ""),
                    "reason": fix.get("reason", "용어 표준화")
                })
        
        # 프로토콜 이슈를 제안으로 변환
        protocol_flags = protocol.get("flags", {})
        if protocol_flags.get("banned_terms"):
            for term in protocol_flags["banned_terms"][:2]:
                protocol_suggestions.append({
                    "category": "프로토콜",
                    "rule": "금칙어 사용",
                    "violation": term,
                    "correction": "대체 표현 사용",
                    "severity": "high"
                })
        
        if not protocol_flags.get("format_ok"):
            missing = protocol.get("details", {}).get("missing_sections", [])
            for section in missing[:2]:
                protocol_suggestions.append({
                    "category": "프로토콜",
                    "rule": "필수 섹션",
                    "violation": f"{section} 누락",
                    "correction": f"{section} 섹션 추가",
                    "severity": "medium"
                })
        
        return {
            # 기본 점수 (모두 텍스트 기반 계산)
            "grammar_score": grammar_score,
            "formality_score": formality_score,
            "readability_score": readability_score,
            "protocol_score": protocol_score,
            "compliance_score": (protocol_score + formality_score) / 2,
            
            # 제안사항
            "suggestions": grammar_suggestions,
            "protocol_suggestions": protocol_suggestions,
            
            # 섹션별 결과
            "grammar_section": {
                "score": grammar_score,
                "feedback": grammar,
                "suggestions": grammar_suggestions
            },
            "protocol_section": {
                "score": protocol_score,
                "feedback": protocol,
                "suggestions": protocol_suggestions
            },
            
            # 메타데이터
            "company_analysis": {
                "company_id": "fallback",
                "communication_style": self._infer_style_from_target(target_audience),
                "compliance_level": protocol_score
            }
        }
    
    def _infer_style_from_target(self, target_audience: str) -> str:
        """대상으로부터 스타일 추론"""
        if target_audience in ["직속상사", "클라이언트", "외부협력업체"]:
            return "formal"
        elif target_audience in ["후배신입"]:
            return "friendly"
        return "formal"
    
    def _create_error_response(
        self, 
        text: str, 
        target_audience: str,
        context: str,
        error_msg: str, 
        start_time: float
    ) -> Dict[str, Any]:
        """오류 응답 생성 - 하드코딩 제거, 텍스트가 있으면 최소 분석"""
        processing_time = asyncio.get_event_loop().time() - start_time
        
        # 텍스트가 있으면 최소한의 분석 시도
        if text and len(text.strip()) >= 5:
            try:
                logger.info("오류 상황에서 최소 분석 시도")
                
                # rewrite_service로 최소 분석
                audience_list = self._map_target_to_audience(target_audience)
                channel = self._map_context_to_channel(context)
                
                rewrite_result = rewrite_text(
                    text=text,
                    traits={},
                    context={
                        "audience": audience_list,
                        "channel": channel
                    },
                    options={"analysis_only": True}
                )
                
                # 변환
                result = self._convert_rewrite_to_enterprise_format(
                    rewrite_result,
                    target_audience,
                    context
                )
                
                result.update({
                    "processing_time": processing_time,
                    "method_used": "error_minimal_analysis",
                    "error": error_msg,
                    "warnings": ["시스템 오류로 최소 분석만 수행됨"]
                })
                
                return result
                
            except Exception as minimal_error:
                logger.error(f"최소 분석도 실패: {minimal_error}")
        
        # 텍스트가 없거나 최소 분석도 실패하면 0점 + 명확한 에러
        return {
            "grammar_score": 0.0,
            "formality_score": 0.0,
            "readability_score": 0.0,
            "protocol_score": 0.0,
            "compliance_score": 0.0,
            "suggestions": [],
            "protocol_suggestions": [],
            "grammar_section": {
                "score": 0.0,
                "suggestions": []
            },
            "protocol_section": {
                "score": 0.0,
                "suggestions": []
            },
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
        """기업용 상세 분석 정보 추가"""
        
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
            },
            'usage_recommendations': {
                'suitable_channels': self._recommend_channels(base_result, context),
                'target_adjustments': self._recommend_target_adjustments(base_result, target_audience),
                'context_optimizations': self._recommend_context_optimizations(base_result, context)
            }
        }
        
        return detailed_info
    
    def _determine_enterprise_improvement_priority(self, result: Dict[str, Any]) -> List[str]:
        """기업용 개선 우선순위 결정"""
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
    
    def _recommend_channels(self, result: Dict[str, Any], context: str) -> List[str]:
        """적합한 채널 추천"""
        score = result.get('compliance_score', 70)
        
        channel_recommendations = {
            "보고서": ["email", "formal_document"] if score >= 80 else ["internal_review"],
            "회의록": ["shared_drive", "team_channel"] if score >= 75 else ["draft_review"],
            "이메일": ["email"] if score >= 70 else ["draft_mode"],
            "공지사항": ["announcement_channel"] if score >= 80 else ["team_review"],
            "메시지": ["instant_message", "chat"] if score >= 65 else ["formal_email"]
        }
        
        return channel_recommendations.get(context, ["review_first"])
    
    def _recommend_target_adjustments(self, result: Dict[str, Any], target_audience: str) -> List[str]:
        """대상별 조정 추천"""
        formality_score = result.get('formality_score', 70)
        target_info = ENTERPRISE_TARGETS.get(target_audience, {})
        required_level = target_info.get('formality_level', 'medium')
        
        if required_level == 'very-high' and formality_score < 85:
            return ["격식도를 매우 높여주세요", "공식적 표현 사용"]
        elif required_level == 'high' and formality_score < 80:
            return ["격식도를 높여주세요", "존댓말 사용"]
        elif required_level == 'medium' and formality_score < 70:
            return ["적절한 격식도 유지", "친근하되 예의바른 표현"]
        
        return ["현재 수준 적절"]
    
    def _recommend_context_optimizations(self, result: Dict[str, Any], context: str) -> List[str]:
        """상황별 최적화 추천"""
        protocol_score = result.get('protocol_score', 70)
        context_info = ENTERPRISE_CONTEXTS.get(context, {})
        required_elements = context_info.get('format_requirements', [])
        
        recommendations = []
        
        if protocol_score < 70:
            recommendations.append(f"{context} 형식 요구사항 준수 필요")
            recommendations.extend([f"포함 필요: {elem}" for elem in required_elements[:2]])
        elif protocol_score < 80:
            recommendations.append(f"{context}에 적합한 구조로 정리")
        else:
            recommendations.append("현재 형식 적절")
        
        return recommendations
    
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
            
            # 피드백 데이터 구성
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
    
    async def generate_final_integrated_text(
        self,
        original_text: str,
        grammar_feedbacks: List[Dict[str, Any]],
        protocol_feedbacks: List[Dict[str, Any]],
        user_selections: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """사용자 피드백 기반 최종 통합본 생성"""
        
        try:
            await self._ensure_initialized()
            
            # 선택된 피드백만 필터링
            selected_grammar = [
                fb for fb in grammar_feedbacks 
                if fb.get('id') in user_selections.get('grammar', [])
            ]
            selected_protocol = [
                fb for fb in protocol_feedbacks 
                if fb.get('id') in user_selections.get('protocol', [])
            ]
            
            # 통합 프롬프트 구성
            integration_prompt = f"""다음 원본 텍스트에 사용자가 선택한 개선사항들을 적용하여 최종 버전을 생성해주세요.

원본 텍스트:
{original_text}

문법 개선사항 (사용자 승인):
{self._format_selected_suggestions(selected_grammar)}

프로토콜 개선사항 (사용자 승인):
{self._format_selected_suggestions(selected_protocol)}

요구사항:
1. 원본의 의도와 핵심 내용을 유지하세요
2. 선택된 개선사항만 적용하세요
3. 자연스럽고 일관성 있는 텍스트로 완성하세요

최종 텍스트:"""
            
            # RAG 서비스로 통합본 생성
            result = await self.rag_service.ask_generative_question(
                query=integration_prompt,
                context="텍스트 통합 최종본 생성"
            )
            
            if result and result.get("success"):
                final_text = result["answer"].strip()
                
                return {
                    "success": True,
                    "final_text": final_text,
                    "applied_suggestions": {
                        "grammar_count": len(selected_grammar),
                        "protocol_count": len(selected_protocol),
                        "total_applied": len(selected_grammar) + len(selected_protocol)
                    },
                    "original_length": len(original_text),
                    "final_length": len(final_text)
                }
            else:
                return {
                    "success": False,
                    "error": "통합본 생성 실패",
                    "final_text": original_text
                }
                
        except Exception as e:
            logger.error(f"최종 통합본 생성 실패: {e}")
            return {
                "success": False,
                "error": str(e),
                "final_text": original_text
            }
    
    def _format_selected_suggestions(self, suggestions: List[Dict[str, Any]]) -> str:
        """선택된 제안사항 포맷팅"""
        if not suggestions:
            return "선택된 개선사항 없음"
        
        formatted = []
        for i, suggestion in enumerate(suggestions, 1):
            formatted.append(
                f"{i}. {suggestion.get('original', '')} → {suggestion.get('suggestion', '')}"
                f" (이유: {suggestion.get('reason', '')})"
            )
        
        return "\n".join(formatted)
    
    # 기업 데이터 관리
    async def get_company_status(self, company_id: str) -> Dict[str, Any]:
        """기업 설정 상태 확인"""
        try:
            await self._ensure_initialized()
            
            if self.db_service is None:
                return {"status": "db_unavailable"}
            
            # 기업 프로필 확인
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