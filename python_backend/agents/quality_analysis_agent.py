"""
Base Agent를 상속한 Quality Analysis Agent
공통 기능은 BaseAgent에서 활용하고 Quality 분석 전용 로직만 구현
"""

from typing import TypedDict, Dict, Any, List
from langgraph.graph import StateGraph, END
from dataclasses import dataclass
from enum import Enum

from agents.base_agent import (
    BaseAgent, BaseAgentState, BaseAgentConfig, BaseAgentResult,
    CommonAgentNodes, AgentFactory, agent_monitor
)

# Quality Agent 전용 상태
class QualityAnalysisState(BaseAgentState):
    """Quality Analysis Agent 전용 상태"""
    text: str
    target_audience: str
    context: str
    grammar_score: float
    formality_score: float
    readability_score: float
    context_feedback: Dict[str, Any]
    target_feedback: Dict[str, Any]
    suggestions: List[Dict[str, str]]

# 맥락별 설정
class ContextType(Enum):
    GENERAL = "일반"
    EDUCATION = "교육"
    OFFICIAL_DOCUMENT = "보고서_공문"  

@dataclass
class ContextConfig:
    name: str
    description: str
    scoring_criteria: Dict[str, str]
    feedback_template: str
    prompt_template: str

# 맥락별 설정 정의
CONTEXT_CONFIGS = {
    ContextType.GENERAL: ContextConfig(
        name="일반",
        description="일상적 소통을 위한 글쓰기",
        scoring_criteria={
            "grammar": "기본적인 문법 규칙 준수",
            "formality": "상황에 맞는 적절한 존댓말 사용",
            "readability": "자연스럽고 이해하기 쉬운 표현"
        },
        feedback_template="일상 소통에서 '{original}' 표현은 {reason}. '{suggestion}'로 바꾸시면 더 자연스럽게 전달됩니다.",
        prompt_template="""일반적인 소통 상황에서 다음 텍스트를 평가해주세요:
- 자연스러운 한국어 표현인가?
- 읽는 사람이 이해하기 쉬운가?
- 적절한 높임말을 사용했는가?

텍스트: {text}"""
    ),
    
    ContextType.EDUCATION: ContextConfig(
        name="교육",
        description="교육 목적의 설명이나 안내문",
        scoring_criteria={
            "grammar": "정확한 문법으로 학습자 혼란 방지",
            "formality": "교육자로서 적절한 격식과 친근함의 균형",
            "readability": "학습자가 이해하기 쉬운 단계적 설명"
        },
        feedback_template="교육 맥락에서 '{original}' 표현은 {reason}. 학습자를 위해 '{suggestion}'로 수정하시면 더 효과적입니다.",
        prompt_template="""교육용 텍스트로서 다음을 평가해주세요:
- 학습자가 이해하기 쉽게 설명되었는가?
- 교육자로서 적절한 어조와 격식을 유지했는가?
- 단계적이고 논리적으로 구성되었는가?
- 어려운 용어에 대한 설명이 충분한가?

텍스트: {text}"""
    ),
    
    ContextType.OFFICIAL_DOCUMENT: ContextConfig(
        name="보고서_공문",
        description="업무용 보고서나 공식 행정 문서",
        scoring_criteria={
            "grammar": "공식 문서로서 완벽한 문법 구사",
            "formality": "업무상 적절한 격식과 공식적 어조",
            "readability": "핵심 내용의 명확하고 체계적인 전달"
        },
        feedback_template="공식 문서에서 '{original}' 표현은 {reason}. 업무 문서의 격식과 명확성을 위해 '{suggestion}'로 수정하는 것이 적절합니다.",
        prompt_template="""공식 업무 문서(보고서_공문)로서 다음을 평가해주세요:
- 객관적이고 정확한 표현을 사용했는가?
- 업무상 적절한 격식과 공식적 어조를 유지했는가?
- 핵심 내용이 명확하고 체계적으로 전달되는가?
- 불필요한 감정 표현이나 비공식적 표현이 없는가?

텍스트: {text}"""
    )
}


@dataclass
class QualityAgentConfig(BaseAgentConfig):
    """Quality Agent 전용 설정"""
    max_suggestions: int = 4
    confidence_threshold: float = 0.6
    enable_detailed_analysis: bool = True

class QualityAnalysisAgent(BaseAgent):
    """Base Agent를 상속한 Quality Analysis Agent"""
    
    def _get_default_config(self) -> QualityAgentConfig:
        """Quality Agent 기본 설정"""
        return QualityAgentConfig(
            name="quality_analysis",
            version="2.0.0",
            timeout=30.0,
            max_retries=3,
            enable_logging=True,
            fallback_enabled=True
        )
    
    def _build_graph(self) -> StateGraph:
        """Quality Analysis 워크플로우 구성"""
        workflow = StateGraph(QualityAnalysisState)
        
        # 노드
        workflow.add_node("initialize", CommonAgentNodes.initialize_step)
        workflow.add_node("context_analysis", self._analyze_context)
        workflow.add_node("target_analysis", self._analyze_target)
        workflow.add_node("scoring", self._calculate_scores)
        workflow.add_node("generate_feedback", self._generate_feedback)
        workflow.add_node("finalize", CommonAgentNodes.finalize_step)
        
        # 엣지
        workflow.set_entry_point("initialize")
        workflow.add_edge("initialize", "context_analysis")
        workflow.add_edge("context_analysis", "target_analysis")
        workflow.add_edge("target_analysis", "scoring")
        workflow.add_edge("scoring", "generate_feedback")
        workflow.add_edge("generate_feedback", "finalize")
        workflow.add_edge("finalize", END)
        
        return workflow.compile()
    
    def _create_initial_state(self, **kwargs) -> QualityAnalysisState:
        """Quality Analysis 초기 상태 생성"""
        return QualityAnalysisState(
            text=kwargs.get('text', ''),
            target_audience=kwargs.get('target_audience', '일반인'),
            context=kwargs.get('context', '일반'),
            current_step='',
            start_time=0.0,
            error_message='',
            rag_sources=[],
            processing_metadata={},
            grammar_score=0.0,
            formality_score=0.0,
            readability_score=0.0,
            context_feedback={},
            target_feedback={},
            suggestions=[]
        )
    
    async def _process_final_result(self, final_state: QualityAnalysisState) -> BaseAgentResult:
        """최종 결과 처리"""
        success = not bool(final_state.get("error_message"))
        
        result_data = {
            "grammar_score": final_state["grammar_score"],
            "formality_score": final_state["formality_score"],
            "readability_score": final_state["readability_score"],
            "suggestions": final_state["suggestions"],
            "context_analysis": final_state["context_feedback"],
            "target_analysis": final_state["target_feedback"]
        }
        
        # 모니터링 기록
        processing_time = final_state["processing_metadata"].get("total_duration", 0)
        agent_monitor.record_execution("quality_analysis", processing_time, success)
        
        return BaseAgentResult(
            success=success,
            data=result_data,
            error=final_state.get("error_message") if not success else None,
            rag_sources_count=len(final_state["rag_sources"]),
            confidence_level=self._determine_confidence_level(final_state)
        )
    
    # Quality Agent 전용 노드 함수들
    async def _analyze_context(self, state: QualityAnalysisState) -> QualityAnalysisState:
        """맥락별 분석 (BaseAgent의 유틸리티 활용)"""
        
        async with self._step_context("맥락 분석", state):
            # 맥락 타입 확인
            context_type = None
            for ctx in ContextType:
                if ctx.value == state["context"]:
                    context_type = ctx
                    break
            
            if not context_type:
                context_type = ContextType.GENERAL
            
            config = CONTEXT_CONFIGS[context_type]
            prompt = self._build_context_prompt(config, state["text"])
            
            # BaseAgent의 retry 로직 활용
            result = await self._call_rag_with_retry(
                prompt=prompt,
                context=f"{config.name} 맥락 분석"
            )
            
            if result:
                try:
                    analysis_data = self._extract_json_from_text(result["answer"])
                    state["context_feedback"] = {
                        "config": config,
                        "analysis": analysis_data,
                        "sources": result.get("sources", [])
                    }
                    state["rag_sources"].extend(result.get("sources", []))
                except Exception as e:
                    self.logger.warning(f"맥락 분석 결과 파싱 실패: {e}")
                    state["error_message"] = f"맥락 분석 결과 처리 실패"
            else:
                state["error_message"] = "맥락 분석 RAG 호출 실패"
        
        return state
    
    async def _analyze_target(self, state: QualityAnalysisState) -> QualityAnalysisState:
        """대상별 분석"""
        
        async with self._step_context("대상 분석", state):
            prompt = f"""'{state['target_audience']}' 대상으로 다음 텍스트의 적합성을 평가해주세요.

분석할 텍스트: {state['text']}

JSON 형식으로 응답:
{{
    "target_appropriateness": <0-100 점수>,
    "vocabulary_level": "어휘 수준 평가",
    "comprehension_difficulty": "이해 난이도 평가",
    "adjustments_needed": [
        {{
            "aspect": "조정이 필요한 측면",
            "reason": "조정이 필요한 이유",
            "suggestion": "구체적인 개선 방안"
        }}
    ]
}}"""
            
            result = await self._call_rag_with_retry(
                prompt=prompt,
                context=f"{state['target_audience']} 대상 분석"
            )
            
            if result:
                try:
                    analysis_data = self._extract_json_from_text(result["answer"])
                    state["target_feedback"] = {
                        "analysis": analysis_data,
                        "sources": result.get("sources", [])
                    }
                    state["rag_sources"].extend(result.get("sources", []))
                except Exception as e:
                    self.logger.warning(f"대상 분석 결과 파싱 실패: {e}")
        
        return state
    
    async def _calculate_scores(self, state: QualityAnalysisState) -> QualityAnalysisState:
        """체계적인 점수 계산 (BaseAgent 유틸리티 활용)"""
        
        async with self._step_context("점수 계산", state):
            # 맥락 분석 점수 추출
            context_score = 70.0
            if state["context_feedback"].get("analysis"):
                raw_score = state["context_feedback"]["analysis"].get("context_score", 70)
                context_score = self._validate_and_normalize_score(raw_score, 70.0)
            
            # 대상 분석 점수 추출
            target_score = 70.0
            if state["target_feedback"].get("analysis"):
                raw_score = state["target_feedback"]["analysis"].get("target_appropriateness", 70)
                target_score = self._validate_and_normalize_score(raw_score, 70.0)
            
            # RAG 신뢰도 기반 가중치
            rag_weight = self._calculate_rag_confidence(state["rag_sources"])
            
            # 최종 점수 계산
            state["grammar_score"] = min(100.0, (context_score * 0.6 + target_score * 0.4) * rag_weight)
            state["formality_score"] = min(100.0, (context_score * 0.7 + target_score * 0.3) * rag_weight)
            state["readability_score"] = min(100.0, (target_score * 0.6 + context_score * 0.4) * rag_weight)
        
        return state
    
    async def _generate_feedback(self, state: QualityAnalysisState) -> QualityAnalysisState:
        """개선된 피드백 생성"""
        
        async with self._step_context("피드백 생성", state):
            suggestions = []
            
            # 맥락별 피드백
            if state["context_feedback"].get("analysis"):
                context_analysis = state["context_feedback"]["analysis"]
                config = state["context_feedback"]["config"]
                
                for issue in context_analysis.get("grammar_issues", []):
                    feedback = config.feedback_template.format(
                        original=issue.get("original", ""),
                        reason=issue.get("reason", ""),
                        suggestion=issue.get("suggestion", "")
                    )
                    suggestions.append({
                        "category": "맥락별 문법",
                        "original": issue.get("original", ""),
                        "suggestion": issue.get("suggestion", ""),
                        "reason": feedback
                    })
            
            # 대상별 피드백
            if state["target_feedback"].get("analysis"):
                target_analysis = state["target_feedback"]["analysis"]
                
                for adjustment in target_analysis.get("adjustments_needed", []):
                    suggestions.append({
                        "category": "대상별 조정",
                        "original": adjustment.get("aspect", ""),
                        "suggestion": adjustment.get("suggestion", ""),
                        "reason": f"{state['target_audience']} 대상으로는 {adjustment.get('reason', '')}"
                    })
            
            # 기본 제안
            if not suggestions:
                suggestions.append({
                    "category": "일반",
                    "original": "전체 텍스트",
                    "suggestion": "더 명확하고 적절한 표현으로 수정",
                    "reason": "구체적인 개선점을 찾지 못했지만 전반적인 개선을 권장합니다"
                })
            
            # 최대 제안 수 제한
            max_suggestions = getattr(self.config, 'max_suggestions', 4)
            state["suggestions"] = suggestions[:max_suggestions]
        
        return state
    
    # 유틸리티 메서드들
    def _build_context_prompt(self, config: ContextConfig, text: str) -> str:
        """맥락별 프롬프트 구성"""
        criteria_text = "\n".join([
            f"- {key}: {desc}" 
            for key, desc in config.scoring_criteria.items()
        ])
        
        return f"""{config.prompt_template.format(text=text)}

평가 기준:
{criteria_text}

다음 JSON 형식으로 응답해주세요:
{{
    "context_score": <0-100 점수>,
    "grammar_issues": [
        {{
            "original": "문제가 있는 표현",
            "issue": "구체적인 문제점",
            "suggestion": "개선된 표현",
            "reason": "{config.name} 맥락에서 부적절한 이유"
        }}
    ],
    "formality_assessment": {{
        "current_level": "현재 격식도 수준",
        "required_level": "{config.name}에 필요한 격식도",
        "adjustments": ["필요한 조정사항들"]
    }},
    "readability_factors": {{
        "sentence_structure": "문장 구조 평가",
        "vocabulary_level": "어휘 수준 평가", 
        "logical_flow": "논리적 흐름 평가"
    }}
}}"""
    
    def _determine_confidence_level(self, state: QualityAnalysisState) -> str:
        """신뢰도 레벨 결정"""
        if state.get("error_message"):
            return "낮음"
        
        sources_count = len(state["rag_sources"])
        if sources_count >= 5:
            return "높음"
        elif sources_count >= 2:
            return "보통"
        else:
            return "낮음"
    
    # 간편한 실행 메서드 (기존 호환성 유지)
    async def analyze(self, text: str, target_audience: str, context: str) -> Dict[str, Any]:
        """기존 인터페이스 유지를 위한 래퍼 메서드"""
        result = await self.execute(
            text=text,
            target_audience=target_audience,
            context=context
        )
        
        if result.success:
            return result.data
        else:
            # 오류 시에도 기존 형태로 반환
            return {
                "grammar_score": 50.0,
                "formality_score": 50.0,
                "readability_score": 50.0,
                "suggestions": [{
                    "category": "오류",
                    "original": "전체 텍스트",
                    "suggestion": "시스템 오류로 분석 실패",
                    "reason": result.error or "알 수 없는 오류"
                }],
                "context_analysis": {},
                "target_analysis": {},
                "rag_sources_count": 0,
                "error": result.error
            }

# Quality Agent를 팩토리에 등록
AgentFactory.register("quality_analysis", QualityAnalysisAgent)

# 편의 함수들
async def analyze_with_agent(
    text: str, 
    target_audience: str, 
    context: str, 
    rag_service
) -> Dict[str, Any]:
    """기존 함수와의 호환성을 위한 래퍼"""
    agent = AgentFactory.create("quality_analysis", rag_service)
    return await agent.analyze(text, target_audience, context)

def create_quality_agent(rag_service, config: QualityAgentConfig = None) -> QualityAnalysisAgent:
    """Quality Agent 생성 함수"""
    return QualityAnalysisAgent(rag_service, config)