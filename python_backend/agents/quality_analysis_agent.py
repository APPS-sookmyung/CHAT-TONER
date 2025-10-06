"""
최적화된 기업용 Quality Analysis Agent
단일 API 호출로 문법 + 프로토콜 통합 분석
Agent 내부 fallback: 규칙 기반 분석 + 경량 LLM 제안
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
    version: str = "1.2.0"
    timeout: float = 35.0
    max_suggestions: int = 4
    max_protocol_suggestions: int = 4
    confidence_threshold: float = 0.6
    enable_comprehensive_analysis: bool = True
    enable_llm_fallback: bool = True  # LLM fallback 사용 여부

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
                    # JSON 파싱
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
        """Agent 내부 규칙 기반 fallback: 분석 + 경량 LLM 제안"""
        from services.rewrite_service import rewrite_text
        
        self.logger.info(f"규칙 기반 분석 + LLM 제안 시작 (이유: {reason})")
        
        # 1단계: rewrite_text로 분석만 수행
        rewrite_result = rewrite_text(
            text=state["text"],
            traits={},
            context={
                "audience": self._map_audience(state["target_audience"]),
                "channel": self._map_channel(state["context"])
            },
            options={"analysis_only": True}  # 재작성 없이 분석만
        )
        
        # 2단계: 점수 계산 (기업 맥락 반영)
        scores = self._calculate_scores_from_analysis(rewrite_result, state["company_profile"])
        
        # 3단계: LLM으로 구체적 제안 생성
        if self.config.enable_llm_fallback:
            suggestions = await self._generate_suggestions_with_llm(
                text=state["text"],
                analysis_result=rewrite_result,
                target_audience=state["target_audience"],
                context=state["context"],
                company_profile=state["company_profile"]
            )
        else:
            # LLM 비활성화 시 기본 제안
            suggestions = self._create_basic_suggestions(rewrite_result)
        
        # 4단계: comprehensive_analysis 구성
        state["comprehensive_analysis"] = {
            "grammar_analysis": {
                "grammar_score": scores["grammar_score"],
                "formality_score": scores["formality_score"],
                "readability_score": scores["readability_score"],
                "grammar_issues": suggestions["grammar"]
            },
            "protocol_analysis": {
                "protocol_score": scores["protocol_score"],
                "compliance_issues": suggestions["protocol"],
                "tone_assessment": {
                    "matches_company_tone": rewrite_result.get("protocol", {}).get("flags", {}).get("tone_consistent", True),
                    "appropriateness": "appropriate",
                    "suggestions": []
                },
                "format_compliance": {
                    "meets_format": rewrite_result.get("protocol", {}).get("flags", {}).get("format_ok", True),
                    "required_elements": rewrite_result.get("protocol", {}).get("details", {}).get("missing_sections", [])
                }
            },
            "overall_assessment": {
                "enterprise_readiness": (scores["grammar_score"] + scores["protocol_score"]) / 2,
                "primary_concerns": self._identify_concerns(scores),
                "strengths": []
            }
        }
        
        state["processing_metadata"]["analysis_method"] = "rule_based_with_llm_suggestions"
        state["processing_metadata"]["fallback_reason"] = reason
        
        self.logger.info("규칙 기반 분석 완료")
        return state
    
    def _calculate_scores_from_analysis(
        self,
        rewrite_result: dict,
        company_profile: dict
    ) -> dict:
        """rewrite 분석 결과 → 점수 계산 (기업 맥락 반영, Expectation-Gap 모델)"""
        
        grammar = rewrite_result.get("grammar", {})
        protocol = rewrite_result.get("protocol", {})
        
        # 1) 기본 점수 추출 (텍스트 절대 평가)
        base_grammar = grammar.get("metrics", {}).get("grammar_score", 70.0)
        base_formality = self._extract_formality_score(grammar)
        base_readability = self._extract_readability_score(grammar)
        base_protocol = protocol.get("metrics", {}).get("policy_score", 0.7) * 100
        
        # 2) 기업 기대치 정의
        company_style = company_profile.get("communication_style", "formal")
        expectations = {
            "strict": {"formality": 90, "protocol": 85},
            "formal": {"formality": 80, "protocol": 75},
            "friendly": {"formality": 70, "protocol": 65}
        }
        expected = expectations.get(company_style, expectations["formal"])
        
        # 3) Expectation-Gap 기반 조정
        # Gap이 클수록 페널티 증가 (낮은 점수일수록 더 큰 페널티)
        formality_gap = max(0, expected["formality"] - base_formality)
        protocol_gap = max(0, expected["protocol"] - base_protocol)
        
        adjusted_formality = base_formality - (formality_gap * 0.2)  # 30% 조정
        adjusted_protocol = base_protocol - (protocol_gap * 0.3)     
        
        adjusted_formality = max(0, min(100, adjusted_formality))
        adjusted_protocol = max(0, min(100, adjusted_protocol))
        
        return {
            "grammar_score": base_grammar,  # 문법은 절대 평가
            "formality_score": adjusted_formality,
            "readability_score": base_readability,  # 가독성도 절대 평가
            "protocol_score": adjusted_protocol
        }
    
    def _extract_formality_score(self, grammar: dict) -> float:
        """격식도 점수 추출"""
        korean_endings = grammar.get("korean_endings", {})
        if korean_endings.get("ending_ok"):
            return 85.0
        
        speech_level = korean_endings.get("speech_level", "기타")
        speech_map = {
            "합쇼체": 80.0,
            "해요체": 75.0,
            "의문형": 78.0,
            "평서/반말": 60.0,
            "기타": 65.0
        }
        return speech_map.get(speech_level, 65.0)
    
    def _extract_readability_score(self, grammar: dict) -> float:
        """가독성 점수 추출 (평균 문장 길이 기반)"""
        avg_len = grammar.get("metrics", {}).get("avg_sentence_len", 30)
        if avg_len < 20: return 90.0
        if avg_len < 30: return 85.0
        if avg_len < 50: return 75.0
        if avg_len < 80: return 65.0
        return 55.0
    
    async def _generate_suggestions_with_llm(
        self,
        text: str,
        analysis_result: dict,
        target_audience: str,
        context: str,
        company_profile: dict
    ) -> dict:
        """경량 LLM으로 구체적 제안 생성"""
        
        grammar = analysis_result.get("grammar", {})
        protocol = analysis_result.get("protocol", {})
        
        # 문제점 요약 (짧게)
        issues_summary = self._summarize_issues(grammar, protocol)
        
        # 경량 프롬프트 (300-500 토큰)
        prompt = f"""다음 텍스트의 문제점을 기반으로 구체적인 수정 제안을 생성해주세요.

원문:
{text}

대상: {target_audience}
상황: {context}
기업 스타일: {company_profile.get("communication_style", "formal")}

감지된 문제:
{issues_summary}

다음 JSON 형식으로만 응답:
{{
    "grammar_suggestions": [
        {{
            "original": "원문에서 문제 있는 구체적 표현",
            "suggestion": "수정된 표현",
            "reason": "수정 이유"
        }}
    ],
    "protocol_suggestions": [
        {{
            "violation": "위반 내용",
            "correction": "수정 방안",
            "severity": "high|medium|low"
        }}
    ]
}}

최대 5개씩만 제안하세요."""
        
        # LLM 호출
        result = await self._call_rag_with_retry(
            prompt=prompt,
            context="제안사항 생성",
            max_retries=1  # fallback이니까 1회만 시도
        )
        
        if result:
            try:
                suggestions_data = self._extract_json_from_text(result["answer"])
                
                return {
                    "grammar": [
                        {
                            "category": "문법",
                            "original": s.get("original", ""),
                            "issue": "문법/명료성",
                            "suggestion": s.get("suggestion", ""),
                            "reason": s.get("reason", "")
                        }
                        for s in suggestions_data.get("grammar_suggestions", [])[:self.config.max_suggestions]
                    ],
                    "protocol": [
                        {
                            "category": "프로토콜",
                            "rule": "프로토콜 위반",
                            "violation": s.get("violation", ""),
                            "correction": s.get("correction", ""),
                            "severity": s.get("severity", "medium")
                        }
                        for s in suggestions_data.get("protocol_suggestions", [])[:self.config.max_protocol_suggestions]
                    ]
                }
            except Exception as e:
                self.logger.error(f"LLM 제안 파싱 실패: {e}")
                # LLM 실패 시 기본 제안
                return self._create_basic_suggestions(analysis_result)
        
        # LLM 완전 실패
        return self._create_basic_suggestions(analysis_result)
    
    def _summarize_issues(self, grammar: dict, protocol: dict) -> str:
        """분석 결과를 LLM이 이해할 수 있게 요약"""
        issues = []
        
        # 점수 기반 체크 추가
        grammar_score = grammar.get("metrics", {}).get("grammar_score", 70)
        if grammar_score < 70:
            issues.append(f"- 전반적 문법 점수 낮음 ({grammar_score:.0f}점)")

        # 어미 문제
        korean_endings = grammar.get("korean_endings", {})
        if not korean_endings.get("ending_ok"):
            issues.append(f"- 어미 격식: {korean_endings.get('speech_level', '부적절')}")
        
        # 금칙어
        banned = protocol.get("flags", {}).get("banned_terms", [])
        if banned:
            issues.append(f"- 금칙어 사용: {', '.join(banned[:3])}")
        
        # 섹션 누락
        missing = protocol.get("details", {}).get("missing_sections", [])
        if missing:
            issues.append(f"- 필수 섹션 누락: {', '.join(missing[:2])}")
        
        # 문장 길이
        avg_len = grammar.get("metrics", {}).get("avg_sentence_len", 0)
        if avg_len > 50:
            issues.append(f"- 문장이 너무 김 (평균 {avg_len}자)")
        
        # 이모지
        emoji_count = grammar.get("word_flags", {}).get("emoji_used", 0)
        if emoji_count > 0:
            issues.append(f"- 이모지 사용 ({emoji_count}개)")
        
        return "\n".join(issues) if issues else "주요 문제점 없음"
    
    def _create_basic_suggestions(self, analysis_result: dict) -> dict:
        """LLM 실패 시 기본 제안 (금칙어와 섹션만)"""
        protocol = analysis_result.get("protocol", {})
        
        suggestions = {
            "grammar": [],
            "protocol": []
        }
        
        # 금칙어 (구체적)
        banned = protocol.get("flags", {}).get("banned_terms", [])
        for i, term in enumerate(banned[:3]):
            suggestions["protocol"].append({
                "category": "프로토콜",
                "rule": "금칙어",
                "violation": term,
                "correction": "대체 표현 사용 필요",
                "severity": "high"
            })
        
        # 섹션 누락
        missing = protocol.get("details", {}).get("missing_sections", [])
        for i, section in enumerate(missing[:2]):
            suggestions["protocol"].append({
                "category": "프로토콜",
                "rule": "필수 섹션",
                "violation": f"{section} 누락",
                "correction": f"{section} 섹션 추가 권장",
                "severity": "medium"
            })
        
        # 문법 제안은 일반적으로만
        if not protocol.get("flags", {}).get("tone_consistent", True):
            suggestions["grammar"].append({
                "category": "톤",
                "original": "[전체 텍스트]",
                "issue": "톤 일관성",
                "suggestion": "격식 있는 표현으로 통일",
                "reason": "비즈니스 커뮤니케이션 톤 유지"
            })
        
        return suggestions
    
    def _identify_concerns(self, scores: dict) -> list:
        """주요 개선점 식별"""
        concerns = []
        
        if scores["protocol_score"] < 70:
            concerns.append("프로토콜 준수")
        if scores["formality_score"] < 70:
            concerns.append("격식도 조정")
        if scores["grammar_score"] < 70:
            concerns.append("문법 개선")
        if scores["readability_score"] < 70:
            concerns.append("가독성 향상")
        
        return concerns or ["전반적 품질 향상"]
    
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
        """분석 결과에서 제안사항 생성 (RAG 형식과 통일)"""
        # 문법 제안
        grammar_issues = state["grammar_feedback"].get("grammar_issues", [])
        state["suggestions"] = [
            {
                "category": issue.get("category", "문법"),
                "original": issue.get("original", ""),
                "issue": issue.get("issue", ""),  # RAG 형식 통일
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
                "rule": issue.get("rule", ""),
                "violation": issue.get("violation", ""),
                "correction": issue.get("correction", ""),
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
        
        analysis_method = state["processing_metadata"].get("analysis_method", "")
        
        # RAG 성공 시 높은 신뢰도
        if analysis_method == "rag_comprehensive":
            return "높음"
        
        # LLM 제안 있으면 보통
        if analysis_method == "rule_based_with_llm_suggestions":
            return "보통"
        
        # 기본 제안만 있으면 낮음
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
        
        return result.data

AgentFactory.register("optimized_enterprise_quality", OptimizedEnterpriseQualityAgent)