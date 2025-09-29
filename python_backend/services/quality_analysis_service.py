"""
기업용 품질분석 서비스 - DB 연동 버전
기존 QualityAnalysisService를 확장하여 기업 기능 추가
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

# 기존 imports
from .rag_service import RAGService

# 새로운 imports
from agents.quality_analysis_agent import OptimizedEnterpriseQualityAgent,OptimizedEnterpriseQualityConfig 
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
    fallback_to_basic: bool = True
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
        
        # 기존 품질분석 서비스 (fallback용)
        self.basic_service = QualityAnalysisService(rag_service)
        
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
                if not self.config.fallback_to_basic:
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
            result['method_used'] = 'enterprise_agent'
            
            # 상세 분석 추가
            if detailed:
                result.update(await self._add_enterprise_detailed_analysis(result, text, target_audience, context))
            
            logger.info(f"기업용 분석 완료 - 소요시간: {processing_time:.2f}초")
            return result
            
        except Exception as e:
            logger.error(f"기업용 분석 실패: {e}")
            
            # Fallback to basic analysis
            if self.config.fallback_to_basic:
                return await self._fallback_analysis(
                    text, target_audience, context, start_time, str(e)
                )
            else:
                return self._create_error_response(text, str(e), start_time)
    
    async def _fallback_analysis(
        self,
        text: str,
        target_audience: str,
        context: str,
        start_time: float,
        error_msg: str
    ) -> Dict[str, Any]:
        """기본 분석으로 Fallback"""
        
        logger.warning(f"기본 분석으로 전환: {error_msg}")
        
        try:
            # 기존 서비스 사용 (대상/상황 매핑 필요)
            mapped_context = self._map_enterprise_to_basic_context(context)
            mapped_target = self._map_enterprise_to_basic_target(target_audience)
            
            basic_result = await self.basic_service.analyze_text_quality(
                text, mapped_target, mapped_context, detailed=False
            )
            
            # 기업용 형태로 변환
            enterprise_result = self._convert_basic_to_enterprise_format(basic_result)
            
            processing_time = asyncio.get_event_loop().time() - start_time
            enterprise_result.update({
                'processing_time': processing_time,
                'method_used': 'fallback_basic',
                'fallback_reason': error_msg
            })
            
            return enterprise_result
            
        except Exception as fallback_error:
            logger.error(f"Fallback 분석도 실패: {fallback_error}")
            return self._create_error_response(text, f"기업용 실패: {error_msg}, Fallback 실패: {str(fallback_error)}", start_time)
    
    def _map_enterprise_to_basic_context(self, enterprise_context: str) -> str:
        """기업용 상황을 기존 상황으로 매핑"""
        mapping = {
            "보고서": "보고서_공문",
            "회의록": "보고서_공문", 
            "이메일": "일반",
            "공지사항": "일반",
            "메시지": "일반"
        }
        return mapping.get(enterprise_context, "일반")
    
    def _map_enterprise_to_basic_target(self, enterprise_target: str) -> str:
        """기업용 대상을 기존 대상으로 매핑"""
        mapping = {
            "직속상사": "상급자",
            "팀동료": "동료",
            "타부서담당자": "동료",
            "클라이언트": "고객",
            "외부협력업체": "파트너",
            "후배신입": "하급자"
        }
        return mapping.get(enterprise_target, "일반인")
    
    def _convert_basic_to_enterprise_format(self, basic_result: Dict[str, Any]) -> Dict[str, Any]:
        """기존 결과를 기업용 형태로 변환"""
        return {
            # 기존 호환성
            "grammar_score": basic_result.get("grammar_score", 70),
            "formality_score": basic_result.get("formality_score", 70),
            "readability_score": basic_result.get("readability_score", 70),
            "suggestions": basic_result.get("suggestions", []),
            
            # 기업용 추가
            "protocol_score": 70.0,
            "compliance_score": 70.0,
            "protocol_suggestions": [],
            
            # 섹션 분리
            "grammar_section": {
                "score": basic_result.get("grammar_score", 70),
                "feedback": {},
                "suggestions": basic_result.get("suggestions", [])
            },
            "protocol_section": {
                "score": 70.0,
                "feedback": {"note": "기본 분석에서는 프로토콜 분석 불가"},
                "suggestions": []
            },
            
            # 메타데이터
            "company_analysis": {
                "company_id": "unknown",
                "communication_style": "formal",
                "compliance_level": 70.0
            }
        }
    
    def _create_error_response(self, text: str, error_msg: str, start_time: float) -> Dict[str, Any]:
        """오류 응답 생성"""
        processing_time = asyncio.get_event_loop().time() - start_time
        
        return {
            "grammar_score": 60.0,
            "formality_score": 60.0,
            "readability_score": 60.0,
            "protocol_score": 60.0,
            "compliance_score": 60.0,
            "suggestions": [],
            "protocol_suggestions": [],
            "grammar_section": {
                "score": 60.0,
                "suggestions": []
            },
            "protocol_section": {
                "score": 60.0,
                "suggestions": []
            },
            "company_analysis": {
                "company_id": "error",
                "communication_style": "unknown",
                "compliance_level": 60.0
            },
            "processing_time": processing_time,
            "method_used": "error",
            "error": error_msg
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
                'feedback_type': feedback_data.get('feedback_type'),  # 'grammar' or 'protocol'
                'feedback_value': feedback_data.get('feedback_value'), # 'good' or 'bad'
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
        user_selections: Dict[str, List[str]]  # {'grammar': ['good_id1', 'good_id2'], 'protocol': ['good_id1']}
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
                    "final_text": original_text  # 원본 반환
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

# 편의 함수들
async def create_enterprise_quality_service(
    rag_service: RAGService,
    enable_protocol_analysis: bool = True
) -> OptimizedEnterpriseQualityService:
    """기업용 품질분석 서비스 생성"""
    
    config = OptimizedEnterpriseQualityServiceConfig(
        enable_enterprise_mode=True,
        enable_protocol_analysis=enable_protocol_analysis,
        fallback_to_basic=True
    )
    
    service = OptimizedEnterpriseQualityService(rag_service, config)
    
    # 초기화 확인
    try:
        await service._ensure_initialized()
        logger.info("기업용 품질분석 서비스 생성 완료")
    except Exception as e:
        logger.warning(f"기업용 서비스 초기화 실패, fallback 모드로 동작: {e}")
    
    return service

# 사용 예시
async def example_usage():
    """사용 예시"""
    from services.rag_service import RAGService 
    
    # RAG 서비스 초기화 
    rag_service = RAGService()  
    
    # 기업용 서비스 생성
    enterprise_service = await create_enterprise_quality_service(rag_service)
    
    # 테스트 기업 설정
    test_setup = await enterprise_service.create_test_setup("test_company")
    print(f"테스트 설정: {test_setup}")
    
    # 텍스트 분석
    result = await enterprise_service.analyze_enterprise_text(
        text="팀장님께 보고드립니다. 프로젝트가 순조롭게 진행되고 있습니다.",
        target_audience="직속상사",
        context="보고서",
        company_id="test_company",
        user_id="test_user",
        detailed=True
    )
    
    print(f"분석 결과: {result}")

if __name__ == "__main__":
    asyncio.run(example_usage())