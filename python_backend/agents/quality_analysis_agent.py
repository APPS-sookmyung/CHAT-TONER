"""
최적화된 기업용 Quality Analysis Agent
RAG 통합 분석 → 실패 시 Agent 내부 Fallback (utils/llm 활용)
"""

from typing import TypedDict, Dict, Any, List, Optional
from langgraph.graph import StateGraph, END
from dataclasses import dataclass
import logging
import json

from .base_agent import (
    BaseAgent, BaseAgentState, BaseAgentConfig, BaseAgentResult,
    CommonAgentNodes, AgentFactory, agent_monitor
)

logger = logging.getLogger('chattoner.quality_analysis_agent')


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
    
    # 분석 결과
    grammar_score: float
    formality_score: float
    readability_score: float
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
    version: str = "1.4.0"
    timeout: float = 35.0
    max_suggestions: int = 4
    max_protocol_suggestions: int = 4
    confidence_threshold: float = 0.6
    enable_llm_fallback: bool = True


class OptimizedEnterpriseQualityAgent(BaseAgent):
    """기업용 품질분석 Agent (RAG + 내부 Fallback)"""
    
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
        """초기 상태 생성"""
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
        """RAG 기반 통합 분석 → 실패 시 Agent 내부 fallback"""
        async with self._step_context("통합 분석", state):
            # 기업 맥락 정보 구성
            company_style = state["company_profile"].get("communication_style", "formal")
            main_channels = state["company_profile"].get("main_channels", [])
            
            # 가이드라인 텍스트 구성 (상위 3개만)
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
                "suggestion": "개선안",
                "reason": "개선 이유"
            }}
        ]
    }},
    "protocol_analysis": {{
        "protocol_score": <0-100>,
        "compliance_issues": [
            {{
                "original": "위반 표현",
                "suggestion": "수정 방안",
                "reason": "위반 이유",
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
            
            # RAG 호출
            result = await self._call_rag_with_retry(
                prompt=comprehensive_prompt,
                context="기업 커뮤니케이션 종합 분석"
            )
            
            if result:
                try:

                    analysis_data = self._extract_json_from_text(result["answer"])
                    state["comprehensive_analysis"] = analysis_data
                    state["rag_sources"].extend(result.get("sources", []))
                    state["processing_metadata"]["analysis_method"] = "rag_comprehensive"
                    
                    self.logger.info("RAG 통합 분석 완료")
                    return state
                    
                except (ValueError, json.JSONDecodeError) as e:
                    # JSON 파싱 실패 → Agent 내부 fallback
                    self.logger.warning(f"JSON 파싱 실패: {e}, Agent 내부 fallback 시작")
            else:
                # RAG 호출 실패 → Agent 내부 fallback
                self.logger.warning("RAG 호출 실패, Agent 내부 fallback 시작")
            
            # Agent 내부 fallback 실행
            return await self._agent_internal_fallback(state)
        
        return state
    
    async def _agent_internal_fallback(self, state: OptimizedEnterpriseQualityState) -> OptimizedEnterpriseQualityState:
        """
        Agent 내부 fallback: 규칙 기반 분석 + LLM 제안
        이미 로드된 company_profile 재사용
        """
        from services.rewrite_service import rewrite_text
        from utils.quality_analysis_utils import (
            extract_base_scores, apply_expectation_gap, 
            map_audience, map_channel, identify_concerns, create_basic_suggestions
        )
        from utils.quality_analysis_llm import generate_suggestions_with_llm
        
        self.logger.info("Agent 내부 fallback 실행 (이미 로드된 기업 데이터 활용)")
        
        # 1) rewrite_text로 분석
        rewrite_result = rewrite_text(
            text=state["text"],
            traits={},
            context={
                "audience": map_audience(state["target_audience"]),
                "channel": map_channel(state["context"])
            },
            options={"analysis_only": True}
        )
        
        # 2) 점수 계산 (이미 로드된 company_profile 활용!)
        base_scores = extract_base_scores(rewrite_result)
        adjusted_scores, adjustment_info = apply_expectation_gap(
            base_scores, 
            state["company_profile"] if state["company_profile"] else None
        )
        
        # 3) LLM 제안 생성
        if self.config.enable_llm_fallback:
            try:
                suggestions = await generate_suggestions_with_llm(
                    rag_service=self.rag_service,
                    text=state["text"],
                    rewrite_result=rewrite_result,
                    target_audience=state["target_audience"],
                    context=state["context"],
                    company_profile=state["company_profile"] if state["company_profile"] else None,
                    max_grammar=self.config.max_suggestions,
                    max_protocol=self.config.max_protocol_suggestions
                )
            except Exception as e:
                self.logger.error(f"LLM 제안 실패: {e}, 기본 제안 사용")

                suggestions = create_basic_suggestions(rewrite_result)
        else:

            suggestions = create_basic_suggestions(rewrite_result)
        
        # 4) comprehensive_analysis 구성
        grammar = rewrite_result.get("grammar", {})
        protocol = rewrite_result.get("protocol", {})
        
        state["comprehensive_analysis"] = {
            "grammar_analysis": {
                "grammar_score": adjusted_scores["grammar_score"],
                "formality_score": adjusted_scores["formality_score"],
                "readability_score": adjusted_scores["readability_score"],
                "grammar_issues": suggestions["grammar"]
            },
            "protocol_analysis": {
                "protocol_score": adjusted_scores["protocol_score"],
                "compliance_issues": suggestions["protocol"],
                "tone_assessment": {
                    "matches_company_tone": protocol.get("flags", {}).get("tone_consistent", True),
                    "appropriateness": "appropriate",
                    "suggestions": []
                },
                "format_compliance": {
                    "meets_format": protocol.get("flags", {}).get("format_ok", True),
                    "required_elements": protocol.get("details", {}).get("missing_sections", [])
                }
            },
            "overall_assessment": {
                "enterprise_readiness": (adjusted_scores["grammar_score"] + adjusted_scores["protocol_score"]) / 2,
                "primary_concerns": identify_concerns(adjusted_scores),
                "strengths": []
            }
        }
        
        state["processing_metadata"]["analysis_method"] = "agent_fallback"
        state["processing_metadata"]["adjustment_info"] = adjustment_info
        
        self.logger.info("Agent 내부 fallback 완료")
        return state
    
    async def _process_analysis_results(self, state: OptimizedEnterpriseQualityState) -> OptimizedEnterpriseQualityState:
        """분석 결과 처리 및 점수 계산"""
        async with self._step_context("결과 처리", state):
            analysis = state["comprehensive_analysis"]
            
            # 분석 결과가 없으면 에러
            if not analysis:
                self.logger.error("분석 결과가 비어있음")
                state["error_message"] = "분석 실패: 결과 없음"
                return state
            
            # 문법 분석 결과 추출
            grammar_analysis = analysis.get("grammar_analysis", {})
            state["grammar_score"] = self._validate_and_normalize_score(
                grammar_analysis.get("grammar_score")
            )
            state["formality_score"] = self._validate_and_normalize_score(
                grammar_analysis.get("formality_score")
            )
            state["readability_score"] = self._validate_and_normalize_score(
                grammar_analysis.get("readability_score")
            )
            state["grammar_feedback"] = grammar_analysis
            
            # 프로토콜 분석 결과 추출
            protocol_analysis = analysis.get("protocol_analysis", {})
            state["protocol_score"] = self._validate_and_normalize_score(
                protocol_analysis.get("protocol_score")
            )
            state["protocol_feedback"] = protocol_analysis
            
            # 전체 평가 추출
            overall = analysis.get("overall_assessment", {})
            state["compliance_score"] = self._validate_and_normalize_score(
                overall.get("enterprise_readiness")
            )
            
            # 제안사항 생성
            self._generate_suggestions_from_analysis(state)
            
            self.logger.info("분석 결과 처리 완료")
        
        return state
    
    def _generate_suggestions_from_analysis(self, state: OptimizedEnterpriseQualityState):
        """분석 결과에서 제안사항 생성"""
        # 문법 제안
        grammar_issues = state["grammar_feedback"].get("grammar_issues", [])
        state["suggestions"] = [
            {
                "category": issue.get("category", "문법"),
                "original": issue.get("original", ""),
                "suggestion": issue.get("suggestion", ""),
                "reason": issue.get("reason", "")
            }
            for issue in grammar_issues[:self.config.max_suggestions]
        ]
        
        # 프로토콜 제안
        compliance_issues = state["protocol_feedback"].get("compliance_issues", [])
        state["protocol_suggestions"] = [
            {
                "category": issue.get("category", "프로토콜"),
                "original": issue.get("original", ""),           # violation → original
                "suggestion": issue.get("suggestion", ""),       # correction → suggestion
                "reason": issue.get("reason", ""),
                "severity": issue.get("severity", "medium")
            }
            for issue in compliance_issues[:self.config.max_protocol_suggestions]
        ]
    
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
                "communication_style": final_state["company_profile"].get("communication_style") if final_state["company_profile"] else "unknown",
                "compliance_level": final_state["compliance_score"],
                "adjustment_info": final_state["processing_metadata"].get("adjustment_info", {})
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
        
        analysis_method = state["processing_metadata"].get("analysis_method", "")
        
        # RAG 성공 시 높은 신뢰도
        if analysis_method == "rag_comprehensive":
            return "높음"
        
        # Agent fallback 시 보통
        if analysis_method == "agent_fallback":
            return "보통"
        
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
        
        # 실패 시에도 에러 명시
        if not result.success:
            return {
                "error": result.error,
                "grammar_score": 0.0,
                "formality_score": 0.0,
                "readability_score": 0.0,
                "protocol_score": 0.0,
                "compliance_score": 0.0,
                "suggestions": [],
                "protocol_suggestions": [],
                "optimization_info": {
                    "api_calls_used": 0,
                    "analysis_method": "error"
                }
            }
        
        output_data = result.data
        output_data['rag_sources_count'] = result.rag_sources_count
        return output_data


AgentFactory.register("optimized_enterprise_quality", OptimizedEnterpriseQualityAgent)