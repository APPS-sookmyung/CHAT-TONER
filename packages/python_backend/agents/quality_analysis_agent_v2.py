# agents/quality_analysis_agent_v2.py

from typing import TypedDict, Dict, Any, List, Optional
from langgraph.graph import StateGraph, END
from agents.base_agent import (
    BaseAgent, BaseAgentConfig, BaseAgentResult, CommonAgentNodes
)
from agents.prompts.builder import build_prompt
from agents.rag.protocol_retriever import ProtocolRetriever
from services.openai_services import OpenAIService
import logging
import time

logger = logging.getLogger(__name__)


class QualityState(TypedDict):
    # base
    current_step: str
    start_time: float
    error_message: str
    rag_sources: List[Dict[str, Any]]
    processing_metadata: Dict[str, Any]
    # 입력
    text: str
    target: str
    context: str
    company_id: Optional[str]
    # static 파일
    grammar_rules: Optional[str]
    readability_rules: Optional[str]
    business_style: Optional[str]
    negative_prompts: Optional[str]
    # RAG
    rag_chunks: Optional[List[str]]
    company_name: Optional[str]
    rag_available: bool
    # LLM
    raw_response: Optional[str]
    parsed_result: Optional[Dict[str, Any]]
    retry_count: int


class QualityAnalysisAgent(BaseAgent):

    def __init__(self, retriever: ProtocolRetriever):
        self.retriever = retriever
        self.openai_service = OpenAIService()
        # BaseAgent.__init__ 에서 rag_service 요구하니까 None으로
        super().__init__(rag_service=None)

    def _get_default_config(self) -> BaseAgentConfig:
        return BaseAgentConfig(
            name="QualityAnalysis",
            version="2.0.0",
            timeout=40.0,
            max_retries=1,
            fallback_enabled=True,
        )

    def _build_graph(self) -> StateGraph:
        g = StateGraph(QualityState)

        g.add_node("initialize",          self._initialize)
        g.add_node("rag_load",            self._rag_load)
        g.add_node("analyze_with_rag",    self._analyze_with_rag)
        g.add_node("analyze_without_rag", self._analyze_without_rag)
        g.add_node("validate",            self._validate)
        g.add_node("finalize",            CommonAgentNodes.finalize_step)

        g.set_entry_point("initialize")
        g.add_edge("initialize", "rag_load")

        g.add_conditional_edges(
            "rag_load",
            lambda s: "with_rag" if s["rag_available"] else "without_rag",
            {
                "with_rag":    "analyze_with_rag",
                "without_rag": "analyze_without_rag",
            }
        )

        g.add_edge("analyze_with_rag",    "validate")
        g.add_edge("analyze_without_rag", "validate")

        g.add_conditional_edges(
            "validate",
            self._route_validate,
            {
                "ok":    "finalize",
                "retry": "analyze_without_rag",
                "fail":  "finalize",
            }
        )

        g.add_edge("finalize", END)
        return g.compile()

    def _create_initial_state(self, **kwargs) -> Dict[str, Any]:
        return {
            "text":             kwargs["text"],
            "target":           kwargs["target"],
            "context":          kwargs["context"],
            "company_id":       kwargs.get("company_id"),
            "grammar_rules":    kwargs.get("grammar_rules"),
            "readability_rules":kwargs.get("readability_rules"),
            "business_style":   kwargs.get("business_style"),
            "negative_prompts": kwargs.get("negative_prompts"),
            "rag_chunks":       None,
            "company_name":     None,
            "rag_available":    False,
            "raw_response":     None,
            "parsed_result":    None,
            "retry_count":      0,
            "error_message":    "",
        }

    # ── 노드 ────────────────────────────────────────────────

    async def _initialize(self, state: QualityState) -> QualityState:
        state["current_step"] = "초기화"
        state["rag_sources"] = []
        state["processing_metadata"] = {
            "start_time": state.get("start_time", time.time()),
            "steps_completed": [],
        }
        return state

    async def _rag_load(self, state: QualityState) -> QualityState:
        state["current_step"] = "RAG 로드"
        try:
            chunks, company_name = await self.retriever.search(
                query=state["text"],
                company_id=state.get("company_id"),
            )
            if chunks:
                state["rag_chunks"]    = chunks
                state["company_name"]  = company_name
                state["rag_available"] = True
                logger.info(f"[RAG] {len(chunks)}개 청크 로드")
            else:
                state["rag_available"] = False
                logger.info("[RAG] 청크 없음 → fallback")
        except Exception as e:
            logger.warning(f"[RAG] 실패: {e} → fallback")
            state["rag_available"] = False
        return state

    async def _analyze_with_rag(self, state: QualityState) -> QualityState:
        state["current_step"] = "LLM 분석 (with RAG)"
        return await self._run_llm(state)

    async def _analyze_without_rag(self, state: QualityState) -> QualityState:
        state["current_step"] = "LLM 분석 (without RAG)"
        # 재시도 케이스: RAG 청크 비움
        state["rag_chunks"]  = None
        state["company_name"] = None
        return await self._run_llm(state)

    async def _run_llm(self, state: QualityState) -> QualityState:
        system_prompt, user_prompt = build_prompt(
            text=state["text"],
            target=state["target"],
            context=state["context"],
            grammar_rules=state.get("grammar_rules"),
            readability_rules=state.get("readability_rules"),
            business_style=state.get("business_style"),
            negative_prompts=state.get("negative_prompts"),
            rag_chunks=state.get("rag_chunks"),
            company_name=state.get("company_name"),
        )
        state["raw_response"] = await self.openai_service.generate_text(
            prompt=user_prompt,
            system=system_prompt,
            temperature=0.3,
            max_tokens=2000,
        )
        return state

    async def _validate(self, state: QualityState) -> QualityState:
        state["current_step"] = "검증"
        try:
            parsed = self._extract_json_from_text(state["raw_response"])
            self._check_schema(parsed)
            state["parsed_result"] = parsed
        except Exception as e:
            logger.warning(f"[Validate] 실패 (retry={state['retry_count']}): {e}")
            state["retry_count"] += 1
            state["error_message"] = str(e)
        return state

    def _check_schema(self, data: Dict[str, Any]):
        for field in ["grammar", "formality", "protocol", "final_text", "summary"]:
            if field not in data:
                raise ValueError(f"필드 누락: {field}")
        for section in ["grammar", "formality", "protocol"]:
            if "score" not in data[section]:
                raise ValueError(f"{section}.score 누락")
            if "issues" not in data[section]:
                raise ValueError(f"{section}.issues 누락")

    def _route_validate(self, state: QualityState) -> str:
        if state.get("parsed_result"):
            return "ok"
        if state["retry_count"] <= self.config.max_retries:
            return "retry"
        return "fail"

    async def _process_final_result(self, final_state: Dict) -> BaseAgentResult:
        parsed = final_state.get("parsed_result")
        if not parsed:
            return BaseAgentResult(
                success=False,
                data={},
                error=final_state.get("error_message", "분석 실패"),
                method_used="error",
            )
        return BaseAgentResult(
            success=True,
            data=parsed,
            method_used="with_rag" if final_state["rag_available"] else "without_rag",
            rag_sources_count=len(final_state.get("rag_chunks") or []),
            confidence_level="high" if final_state["rag_available"] else "medium",
        )