"""
최적화된 기업용 Quality Analysis Agent
단일 API 호출로 문법 + 프로토콜 통합 분석
Agent 내부 fallback 포함
"""

from typing import TypedDict, Dict, Any, List, Optional
from langgraph.graph import StateGraph, END
from dataclasses import dataclass
import json
import asyncio

from .base_agent import (
    BaseAgent, BaseAgentState, BaseAgentConfig, BaseAgentResult,
    CommonAgentNodes, AgentFactory, agent_monitor
)

class OptimizedEnterpriseQualityState(BaseAgentState):
    """기업용 Quality Analysis Agent 전용 상태"""
    # 기본 입력
    text: str
    target_audience: str
    context: str
    company_id: str
    user_id: str
    
    # 기업 정보
    company_profile: Dict[str, Any]
    company_guidelines: List[Dict[str, Any]]
    user_preferences: Dict[str, Any]
    
    # 통합 분석 결과
    comprehensive_analysis: Dict[str, Any]  
    
    # 분석 결과 (기존)
    grammar_score: float
    formality_score: float
    readability_score: float
    
    # 새로운 분석 결과 (기업용)
    protocol_score: float
    compliance_score: float
    
    # 피드백
    grammar_feedback: Dict[str, Any]
    protocol_feedback: Dict[str, Any]
    suggestions: List[Dict[str, str]]
    protocol_suggestions: List[Dict[str, str]]

@dataclass
class OptimizedEnterpriseQualityConfig(BaseAgentConfig):
    """기업용 Quality Agent 설정"""
    name: str = "optimized_enterprise_quality"
    version: str = "1.1.0"
    timeout: float = 35.0
    max_suggestions: int = 4
    max_protocol_suggestions: int = 4
    confidence_threshold: float = 0.6
    enable_comprehensive_analysis: bool = True

class OptimizedEnterpriseQualityAgent(BaseAgent):
    """기업용 품질분석 Agent"""
    
    def __init__(self, rag_service, db_service, config: Optional[OptimizedEnterpriseQualityConfig] = None):
        super().__init__(rag_service, config or OptimizedEnterpriseQualityConfig())
        self.db_service = db_service
    
    def _build_graph(self) -> StateGraph:
        """워크플로우"""
        workflow = StateGraph(OptimizedEnterpriseQualityState)
        
        # 노드 정의 
        workflow.add_node("initialize", CommonAgentNodes.initialize_step)
        workflow.add_node("load_company_data", self._load_company_data)
        workflow.add_node("comprehensive_analysis", self._comprehensive_analysis)
        workflow.add_node("process_results", self._process_analysis_results)
        workflow.add_node("finalize", CommonAgentNodes.finalize_step)
        
        # 워크플로우 연결 
        workflow.set_entry_point("initialize")
        workflow.add_edge("initialize", "load_company_data")
        workflow.add_edge("load_company_data", "comprehensive_analysis")
        workflow.add_edge("comprehensive_analysis", "process_results")
        workflow.add_edge("process_results", "finalize")
        workflow.add_edge("finalize", END)
        
        return workflow.compile()
    
    def _create_initial_state(self, **kwargs) -> OptimizedEnterpriseQualityState:
        """최적화된 초기 상태 생성"""
        return OptimizedEnterpriseQualityState(
            # 기본 입력
            text=kwargs.get('text', ''),
            target_audience=kwargs.get('target_audience', '팀동료'),
            context=kwargs.get('context', '메시지'),
            company_id=kwargs.get('company_id', ''),
            user_id=kwargs.get('user_id', ''),
            
            # BaseAgent 필수 필드
            current_step='',
            start_time=0.0,
            error_message='',
            rag_sources=[],
            processing_metadata={},
            
            # 기업 데이터
            company_profile={},
            company_guidelines=[],
            user_preferences={},
            
            # 통합 분석 결과
            comprehensive_analysis={},
            
            # 점수 초기화
            grammar_score=0.0,
            formality_score=0.0,
            readability_score=0.0,
            protocol_score=0.0,
            compliance_score=0.0,
            
            # 피드백 초기화
            grammar_feedback={},
            protocol_feedback={},
            suggestions=[],
            protocol_suggestions=[]
        )
    
    def _get_default_config(self) -> OptimizedEnterpriseQualityConfig:
        """기본 설정 반환"""
        return OptimizedEnterpriseQualityConfig()
    
    async def _load_company_data(self, state: OptimizedEnterpriseQualityState) -> OptimizedEnterpriseQualityState:
        """기업 데이터 로딩"""
        async with self._step_context("기업 데이터 로딩", state):
            try:
                # 기업 프로필 로딩
                company_profile = await self.db_service.get_company_profile(state["company_id"])
                state["company_profile"] = company_profile or {}
                
                # 기업 가이드라인 로딩  
                guidelines = await self.db_service.get_company_guidelines(state["company_id"])
                state["company_guidelines"] = guidelines or []
                
                # 사용자 선호도 로딩
                preferences = await self.db_service.get_user_preferences(
                    state["user_id"], state["company_id"]
                )
                state["user_preferences"] = preferences or {}
                
                self.logger.info(f"기업 데이터 로딩 완료 - 가이드라인: {len(state['company_guidelines'])}개")
                
            except Exception as e:
                self.logger.error(f"기업 데이터 로딩 실패: {e}")
                # 로딩 실패해도 기본 분석은 진행
        
        return state
    
    async def _comprehensive_analysis(self, state: OptimizedEnterpriseQualityState) -> OptimizedEnterpriseQualityState:
        """통합 분석 with 내부 fallback"""
        async with self._step_context("통합 분석", state):
            # @@ 클로드가 프롬프트 길이 최적화 필요하대요: 현재 228줄의 긴 프롬프트는 토큰 낭비 및 성능 저하 원인
            # 기업 맥락 정보 구성
            company_style = state["company_profile"].get("communication_style", "formal")
            main_channels = state["company_profile"].get("main_channels", [])
            
            # 가이드라인 텍스트 구성
            guidelines_text = "기본 비즈니스 커뮤니케이션 규칙"
            if state["company_guidelines"]:
                guidelines_text = "\n".join([
                    f"- {g.get('document_name', '')}: {g.get('document_content', '')[:300]}..."
                    for g in state["company_guidelines"][:3]
                ])
            
            # 통합 프롬프트 구성
            comprehensive_prompt = f"""기업 커뮤니케이션 맥락에서 다음 텍스트를 문법과 프로토콜 측면에서 종합 분석해주세요.

기업 정보:
- 커뮤니케이션 스타일: {company_style}
- 주요 채널: {main_channels}
- 대상: {state['target_audience']}
- 상황: {state['context']}

기업 가이드라인:
{guidelines_text}

분석할 텍스트:
{state['text']}

다음 JSON 형식으로 응답해주세요:
{{
    "grammar_analysis": {{
        "grammar_score": <0-100>,
        "formality_score": <0-100>,
        "readability_score": <0-100>,
        "grammar_issues": [
            {{
                "original": "문제 표현",
                "issue": "문제점",
                "suggestion": "개선안",
                "reason": "개선 이유"
            }}
        ]
    }},
    "protocol_analysis": {{
        "protocol_score": <0-100>,
        "compliance_issues": [
            {{
                "rule": "위반된 규칙",
                "violation": "위반 내용",
                "correction": "수정 방안",
                "severity": "high|medium|low"
            }}
        ],
        "tone_assessment": {{
            "matches_company_tone": true/false,
            "appropriateness": "appropriate|too_formal|too_casual",
            "suggestions": ["톤 조정 제안들"]
        }},
        "format_compliance": {{
            "meets_format": true/false,
            "required_elements": ["누락된 필수 요소들"]
        }}
    }},
    "overall_assessment": {{
        "enterprise_readiness": <0-100>,
        "primary_concerns": ["주요 개선점들"],
        "strengths": ["잘된 부분들"]
    }}
}}"""
            
            # 단일 RAG 호출
            result = await self._call_rag_with_retry(
                prompt=comprehensive_prompt,
                context="기업 커뮤니케이션 종합 분석"
            )
            
            if result:
                try:
                    # JSON 파싱 (BaseAgent 메서드 사용)
                    analysis_data = self._extract_json_from_text(result["answer"])
                    state["comprehensive_analysis"] = analysis_data
                    state["rag_sources"].extend(result.get("sources", []))
                    state["processing_metadata"]["analysis_method"] = "rag_comprehensive"
                    
                    self.logger.info("RAG 통합 분석 완료")
                    return state
                    
                except (ValueError, json.JSONDecodeError) as e:
                    # JSON 파싱 실패 → Agent 내부 fallback
                    self.logger.warning(f"JSON 파싱 실패: {e}")
                    return await self._agent_fallback_to_rule_based(state, f"JSON 파싱 실패: {e}")
            
            # RAG 호출 실패 → Agent 내부 fallback
            self.logger.warning("RAG 호출 실패")
            return await self._agent_fallback_to_rule_based(state, "RAG 호출 실패")
        
        return state
    
    async def _agent_fallback_to_rule_based(
        self, 
        state: OptimizedEnterpriseQualityState,
        reason: str
    ) -> OptimizedEnterpriseQualityState:
        """Agent 내부 규칙 기반 fallback"""
        from services.rewrite_service import rewrite_text
        
        try:
            self.logger.info(f"Agent 내부 규칙 기반 분석 시작 (이유: {reason})")
            
            # rewrite_text 실행
            rewrite_result = rewrite_text(
                text=state["text"],
                traits={},
                context={
                    "audience": self._map_audience(state["target_audience"]),
                    "channel": self._map_channel(state["context"])
                },
                options={"strict_policy": False}
            )
            
            # 결과 변환
            state["comprehensive_analysis"] = self._convert_rewrite_to_analysis(rewrite_result)
            state["processing_metadata"]["analysis_method"] = "agent_rule_based_fallback"
            state["processing_metadata"]["fallback_reason"] = reason
            
            self.logger.info("Agent 규칙 기반 분석 완료")
            return state
            
        except Exception as e:
            # Agent 내부 fallback도 실패 → 최소값
            self.logger.error(f"Agent 규칙 기반도 실패: {e}")
            state["comprehensive_analysis"] = self._minimal_analysis()
            state["processing_metadata"]["analysis_method"] = "agent_minimal_fallback"
            state["error_message"] = f"Agent 분석 실패: {reason}, Fallback 실패: {e}"
            return state
    
    def _map_audience(self, target: str) -> list:
        """대상 매핑"""
        mapping = {
            "직속상사": ["executives"],
            "팀동료": ["team"],
            "타부서담당자": ["team"],
            "클라이언트": ["clients_vendors"],
            "외부협력업체": ["clients_vendors"],
            "후배신입": ["team"]
        }
        return mapping.get(target, ["team"])
    
    def _map_channel(self, context: str) -> str:
        """채널 매핑"""
        mapping = {
            "보고서": "report",
            "회의록": "meeting_minutes",
            "이메일": "email",
            "공지사항": "email",
            "메시지": "chat"
        }
        return mapping.get(context, "email")
    
    def _convert_rewrite_to_analysis(self, rewrite_result: dict) -> dict:
        """rewrite 결과 → Agent 분석 형식 변환"""
        grammar = rewrite_result.get("grammar", {})
        protocol = rewrite_result.get("protocol", {})
        
        grammar_score = grammar.get("metrics", {}).get("grammar_score", 70.0)
        korean_endings = grammar.get("korean_endings", {})
        formality_score = 85.0 if korean_endings.get("ending_ok") else 70.0
        
        avg_len = grammar.get("metrics", {}).get("avg_sentence_len", 30)
        readability_score = 90.0 if avg_len < 20 else (75.0 if avg_len < 50 else 60.0)
        
        protocol_score = protocol.get("metrics", {}).get("policy_score", 0.7) * 100
        
        return {
            "grammar_analysis": {
                "grammar_score": grammar_score,
                "formality_score": formality_score,
                "readability_score": readability_score,
                "grammar_issues": []
            },
            "protocol_analysis": {
                "protocol_score": protocol_score,
                "compliance_issues": [],
                "tone_assessment": {
                    "matches_company_tone": True,
                    "appropriateness": "appropriate",
                    "suggestions": []
                },
                "format_compliance": {
                    "meets_format": True,
                    "required_elements": []
                }
            },
            "overall_assessment": {
                "enterprise_readiness": (grammar_score + formality_score + protocol_score) / 3,
                "primary_concerns": ["규칙 기반 분석 결과"],
                "strengths": []
            }
        }
    
    def _minimal_analysis(self) -> dict:
        """최소 기본값"""
        return {
            "grammar_analysis": {
                "grammar_score": 60.0,
                "formality_score": 60.0,
                "readability_score": 60.0,
                "grammar_issues": []
            },
            "protocol_analysis": {
                "protocol_score": 60.0,
                "compliance_issues": [],
                "tone_assessment": {},
                "format_compliance": {}
            },
            "overall_assessment": {
                "enterprise_readiness": 60.0,
                "primary_concerns": ["Agent 분석 실패"],
                "strengths": []
            }
        }
    
    async def _process_analysis_results(self, state: OptimizedEnterpriseQualityState) -> OptimizedEnterpriseQualityState:
        """분석 결과 처리 및 점수 계산"""
        async with self._step_context("결과 처리", state):
            analysis = state["comprehensive_analysis"]
            
            if not analysis:
                # 기본값으로 설정
                state["grammar_score"] = 60.0
                state["formality_score"] = 60.0
                state["readability_score"] = 60.0
                state["protocol_score"] = 60.0
                state["compliance_score"] = 60.0
                return state
            
            # 문법 분석 결과 추출
            grammar_analysis = analysis.get("grammar_analysis", {})
            state["grammar_score"] = self._validate_and_normalize_score(
                grammar_analysis.get("grammar_score", 70)
            )
            state["formality_score"] = self._validate_and_normalize_score(
                grammar_analysis.get("formality_score", 70)
            )
            state["readability_score"] = self._validate_and_normalize_score(
                grammar_analysis.get("readability_score", 70)
            )
            state["grammar_feedback"] = grammar_analysis
            
            # 프로토콜 분석 결과 추출
            protocol_analysis = analysis.get("protocol_analysis", {})
            state["protocol_score"] = self._validate_and_normalize_score(
                protocol_analysis.get("protocol_score", 80)
            )
            state["protocol_feedback"] = protocol_analysis
            
            # 전체 평가 추출
            overall = analysis.get("overall_assessment", {})
            state["compliance_score"] = self._validate_and_normalize_score(
                overall.get("enterprise_readiness", 75)
            )
            
            # 제안사항 생성
            self._generate_suggestions_from_analysis(state)
            
            # 기업 맥락 반영한 점수 조정
            self._apply_company_adjustments(state)
            
            self.logger.info("분석 결과 처리 완료")
        
        return state
    
    def _generate_suggestions_from_analysis(self, state: OptimizedEnterpriseQualityState):
        """분석 결과에서 제안사항 생성"""
        # 문법 제안
        grammar_issues = state["grammar_feedback"].get("grammar_issues", [])
        state["suggestions"] = [
            {
                "category": "문법",
                "original": issue.get("original", ""),
                "suggestion": issue.get("suggestion", ""),
                "reason": issue.get("reason", "")
            }
            for issue in grammar_issues[:self.config.max_suggestions]
        ]
        
        # 프로토콜 제안
        compliance_issues = state["protocol_feedback"].get("compliance_issues", [])
        protocol_suggestions = [
            {
                "category": "프로토콜",
                "rule": issue.get("rule", ""),
                "violation": issue.get("violation", ""),
                "correction": issue.get("correction", ""),
                "severity": issue.get("severity", "medium")
            }
            for issue in compliance_issues[:self.config.max_protocol_suggestions]
        ]
        
        # 톤 제안 추가
        tone_assessment = state["protocol_feedback"].get("tone_assessment", {})
        tone_suggestions = tone_assessment.get("suggestions", [])
        for suggestion in tone_suggestions[:2]:
            protocol_suggestions.append({
                "category": "톤앤매너",
                "rule": "기업 커뮤니케이션 스타일",
                "violation": "톤 일관성",
                "correction": suggestion,
                "severity": "medium"
            })
        
        state["protocol_suggestions"] = protocol_suggestions
    
    def _apply_company_adjustments(self, state: OptimizedEnterpriseQualityState):
        """기업 맥락 반영한 점수 조정"""
        company_style = state["company_profile"].get("communication_style", "formal")

        # @@ 점수 조정 로직 부족: 단순 곱셈만으로는 기업별 특성 반영 한계
        # 기업 스타일별 조정
        style_multipliers = {
            "strict": 0.9,    
            "formal": 1.0,    
            "friendly": 1.05  
        }
        
        multiplier = style_multipliers.get(company_style, 1.0)
        
        # RAG 신뢰도 반영
        rag_confidence = self._calculate_rag_confidence(state["rag_sources"])
        
        # 최종 조정
        state["grammar_score"] = min(100.0, state["grammar_score"] * multiplier)
        state["formality_score"] = min(100.0, state["formality_score"] * multiplier)
        state["readability_score"] = min(100.0, state["readability_score"] * multiplier)
        state["protocol_score"] = min(100.0, state["protocol_score"] * multiplier * rag_confidence)
        state["compliance_score"] = min(100.0, state["compliance_score"] * multiplier * rag_confidence)
    
    async def _process_final_result(self, final_state: OptimizedEnterpriseQualityState) -> BaseAgentResult:
        """최종 결과 처리"""
        success = not bool(final_state.get("error_message"))
        
        result_data = {
            # 기존 호환성 유지
            "grammar_score": final_state["grammar_score"],
            "formality_score": final_state["formality_score"], 
            "readability_score": final_state["readability_score"],
            "suggestions": final_state["suggestions"],
            
            # 기업용 새로운 필드
            "protocol_score": final_state["protocol_score"],
            "compliance_score": final_state["compliance_score"],
            "protocol_suggestions": final_state["protocol_suggestions"],
            
            # 섹션별 분리된 결과
            "grammar_section": {
                "score": final_state["grammar_score"],
                "feedback": final_state["grammar_feedback"],
                "suggestions": final_state["suggestions"]
            },
            "protocol_section": {
                "score": final_state["protocol_score"],
                "feedback": final_state["protocol_feedback"],
                "suggestions": final_state["protocol_suggestions"]
            },
            
            # 메타데이터
            "company_analysis": {
                "company_id": final_state["company_id"],
                "communication_style": final_state["company_profile"].get("communication_style"),
                "compliance_level": final_state["compliance_score"]
            },
            
            # 최적화 정보
            "optimization_info": {
                "api_calls_used": 1 if final_state["processing_metadata"].get("analysis_method") == "rag_comprehensive" else 0,
                "analysis_method": final_state["processing_metadata"].get("analysis_method", "unknown")
            }
        }
        
        # 모니터링
        processing_time = final_state["processing_metadata"].get("total_duration", 0)
        agent_monitor.record_execution("optimized_enterprise_quality", processing_time, success)
        
        return BaseAgentResult(
            success=success,
            data=result_data,
            error=final_state.get("error_message") if not success else None,
            rag_sources_count=len(final_state["rag_sources"]),
            confidence_level=self._determine_enterprise_confidence(final_state)
        )
    
    def _determine_enterprise_confidence(self, state: OptimizedEnterpriseQualityState) -> str:
        """기업용 신뢰도 결정"""
        if state.get("error_message"):
            return "낮음"
        
        # 통합 분석의 완성도 평가
        analysis_completeness = bool(state["comprehensive_analysis"])
        company_data_availability = bool(state["company_profile"]) and bool(state["company_guidelines"])
        rag_source_quality = len(state["rag_sources"]) >= 2
        
        confidence_factors = [analysis_completeness, company_data_availability, rag_source_quality]
        score = sum(confidence_factors)
        
        if score >= 3:
            return "높음"
        elif score >= 2:
            return "보통"
        else:
            return "낮음"
    
    # 외부 인터페이스
    async def analyze_enterprise_quality(
        self,
        text: str,
        target_audience: str,
        context: str,
        company_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """최적화된 기업용 품질 분석"""
        result = await self.execute(
            text=text,
            target_audience=target_audience,
            context=context,
            company_id=company_id,
            user_id=user_id
        )
        
        return result.data if result.success else {
            "error": result.error,
            "grammar_score": 60.0,
            "protocol_score": 60.0,
            "suggestions": [],
            "protocol_suggestions": [],
            "optimization_info": {
                "api_calls_used": 0,
                "analysis_method": "error"
            }
        }

# 팩토리 등록
AgentFactory.register("optimized_enterprise_quality", OptimizedEnterpriseQualityAgent)