"""
Base Agent Framework
모든 Agent들이 공통으로 사용할 기반 클래스와 유틸리티
"""

from abc import ABC, abstractmethod
from typing import TypedDict, Dict, Any, List, Optional, Type, Union
from langgraph.graph import StateGraph, END
from dataclasses import dataclass
import asyncio
import logging
import json
import re
import time
from contextlib import asynccontextmanager

# 공통 상태 기반 클래스
class BaseAgentState(TypedDict):
    """모든 Agent가 공통으로 사용할 기본 상태"""
    current_step: str
    start_time: float
    error_message: str
    rag_sources: List[Dict[str, Any]]
    processing_metadata: Dict[str, Any]

# Agent 설정 기반 클래스
@dataclass
class BaseAgentConfig:
    """Agent 공통 설정"""
    name: str
    version: str = "1.0.0"
    timeout: float = 40.0 # 40초 내 작업 끝내지 못하면 실행 중지
    max_retries: int = 2 # 재시도 횟수 일단 2번
    enable_logging: bool = True 
    fallback_enabled: bool = True

# Agent 결과 기반 클래스
@dataclass
class BaseAgentResult:
    """Agent 실행 결과 기반 구조"""
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None
    processing_time: float = 0.0
    method_used: str = "unknown"
    rag_sources_count: int = 0
    confidence_level: str = "medium"

class AgentExecutionError(Exception):
    """Agent 실행 중 발생하는 오류"""
    pass

class BaseAgent(ABC):
    """모든 Agent의 기반 클래스"""
    
    def __init__(self, rag_service, config: Optional[BaseAgentConfig] = None):
        self.rag_service = rag_service
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger(f'agent.{self.config.name}')
        self.graph = None
        
        if self.config.enable_logging:
            self.logger.info(f"{self.config.name} Agent 초기화 완료")
    
    @abstractmethod
    def _get_default_config(self) -> BaseAgentConfig:
        """각 Agent별 기본 설정 정의"""
        pass
    
    @abstractmethod
    def _build_graph(self) -> StateGraph:
        """Agent별 LangGraph 워크플로우 구성"""
        pass
    
    @abstractmethod
    def _create_initial_state(self, **kwargs) -> Dict[str, Any]:
        """Agent별 초기 상태 생성"""
        pass
    
    @abstractmethod
    async def _process_final_result(self, final_state: Dict[str, Any]) -> BaseAgentResult:
        """최종 결과 처리"""
        pass
    
    def initialize(self):
        """Agent 초기화 (그래프 구성) - 성능 최적화: 한번만 빌드"""
        if self.graph is None:
            self.graph = self._build_graph()
            self.logger.info(f"{self.config.name} 워크플로우 구성 완료")
        else:
            self.logger.debug(f"{self.config.name} 워크플로우 재사용 (성능 최적화)")
    
    async def execute(self, **kwargs) -> BaseAgentResult:
        """Agent 실행 (공통 실행 패턴)"""
        start_time = time.time()
        
        try:
            # 초기화 확인
            self.initialize()
            
            # 초기 상태 생성
            initial_state = self._create_initial_state(**kwargs)
            initial_state.update({
                'current_step': '시작',
                'start_time': start_time,
                'error_message': '',
                'rag_sources': [],
                'processing_metadata': {}
            })
            
            # 타임아웃과 함께 그래프 실행
            final_state = await asyncio.wait_for(
                self.graph.ainvoke(initial_state),
                timeout=self.config.timeout
            )
            
            # 결과 처리
            result = await self._process_final_result(final_state)
            result.processing_time = time.time() - start_time
            
            self.logger.info(f"{self.config.name} 실행 완료 - 소요시간: {result.processing_time:.2f}초")
            return result
            
        except asyncio.TimeoutError:
            error_msg = f"{self.config.name} 실행 타임아웃 ({self.config.timeout}초)"
            self.logger.error(error_msg)
            return self._create_error_result(error_msg, time.time() - start_time)
        
        except Exception as e:
            error_msg = f"{self.config.name} 실행 중 오류: {str(e)}"
            self.logger.error(error_msg)
            return self._create_error_result(error_msg, time.time() - start_time)
    
    def _create_error_result(self, error_msg: str, processing_time: float) -> BaseAgentResult:
        """오류 결과 생성"""
        return BaseAgentResult(
            success=False,
            data={},
            error=error_msg,
            processing_time=processing_time,
            method_used="error"
        )
    
    # 공통 유틸리티 메서드들
    async def _call_rag_with_retry(self, prompt: str, context: str, max_retries: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """재시도 로직이 있는 RAG 호출"""
        retries = max_retries or self.config.max_retries # 현 max는 두 번인데, 함수 호출할 때 max_retries 지정 가능
        
        for attempt in range(retries + 1):
            try:
                result = await self.rag_service.ask_generative_question(
                    query=prompt,
                    context=context
                )
                
                if result and result.get("success"):
                    return result
                else:
                    self.logger.warning(f"RAG 호출 실패 (시도 {attempt + 1}/{retries + 1})")
                    
            except Exception as e:
                self.logger.error(f"RAG 호출 오류 (시도 {attempt + 1}/{retries + 1}): {e}")
                
                if attempt < retries:
                    await asyncio.sleep(1.0 * (attempt + 1))  # 지수 백오프
        
        return None
    
    def _extract_json_from_text(self, text: str) -> Dict[str, Any]:
        """텍스트에서 JSON 추출 (공통 로직)"""
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            pass
        
        # JSON 블록 찾기
        json_block_match = re.search(r'```json\s*\n(.*?)\n```', text, re.DOTALL)
        if json_block_match:
            try:
                return json.loads(json_block_match.group(1).strip())
            except json.JSONDecodeError:
                pass
        
        # 중괄호 사이의 JSON 찾기
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        
        raise ValueError("유효한 JSON을 찾을 수 없습니다")
    
    def _validate_and_normalize_score(self, score: Any, default: float = 50.0) -> float:
        """점수 검증 및 정규화"""
        try:
            score_float = float(score)
            return max(0.0, min(100.0, score_float))
        except (ValueError, TypeError):
            self.logger.warning(f"잘못된 점수 형식: {score}, 기본값 {default} 사용")
            return default
    
    def _calculate_rag_confidence(self, sources: List[Dict[str, Any]]) -> float:
        """RAG 신뢰도 계산"""
        if not sources:
            return 0.7
        
        similarities = []
        for source in sources:
            if 'similarity' in source:
                try:
                    similarities.append(float(source['similarity']))
                except (ValueError, TypeError):
                    continue
        
        if similarities:
            avg_similarity = sum(similarities) / len(similarities)
            return 0.7 + (avg_similarity * 0.5)
        
        return 0.8
    
    @asynccontextmanager
    async def _step_context(self, step_name: str, state: Dict[str, Any]):
        """단계별 실행 컨텍스트 관리"""
        state['current_step'] = step_name
        step_start = time.time()
        
        try:
            self.logger.debug(f"{step_name} 단계 시작")
            yield state
            step_duration = time.time() - step_start
            self.logger.debug(f"{step_name} 단계 완료 - 소요시간: {step_duration:.2f}초")
        
        except Exception as e:
            step_duration = time.time() - step_start
            error_msg = f"{step_name} 단계 실패: {str(e)}"
            state['error_message'] = error_msg
            self.logger.error(f"{error_msg} - 소요시간: {step_duration:.2f}초")
            raise

# 공통 노드 함수들
class CommonAgentNodes:
    """Agent들이 공통으로 사용할 노드 함수들"""
    
    @staticmethod
    async def initialize_step(state: BaseAgentState) -> BaseAgentState:
        """공통 초기화 단계"""
        state["current_step"] = "초기화"
        state["rag_sources"] = []
        state["processing_metadata"] = {
            "steps_completed": [],
            "start_time": state.get("start_time", time.time())
        }
        return state
    
    @staticmethod
    async def finalize_step(state: BaseAgentState) -> BaseAgentState:
        """공통 마무리 단계"""
        state["current_step"] = "완료"
        state["processing_metadata"]["end_time"] = time.time()
        state["processing_metadata"]["total_duration"] = (
            state["processing_metadata"]["end_time"] - 
            state["processing_metadata"]["start_time"]
        )
        return state

# Agent 팩토리
class AgentFactory:
    """Agent 인스턴스 생성 및 관리"""
    
    _agents: Dict[str, Type[BaseAgent]] = {}
    
    @classmethod
    def register(cls, name: str, agent_class: Type[BaseAgent]):
        """Agent 클래스 등록"""
        cls._agents[name] = agent_class
    
    @classmethod
    def create(cls, name: str, rag_service, config: Optional[BaseAgentConfig] = None) -> BaseAgent:
        """등록된 Agent 생성"""
        if name not in cls._agents:
            raise ValueError(f"Agent '{name}'이 등록되지 않았습니다")
        
        agent_class = cls._agents[name]
        return agent_class(rag_service, config)
    
    @classmethod
    def list_agents(cls) -> List[str]:
        """등록된 Agent 목록"""
        return list(cls._agents.keys())

# Agent 상태 모니터링
class AgentMonitor:
    """Agent 실행 상태 모니터링"""
    
    def __init__(self):
        self.execution_stats: Dict[str, List[float]] = {}
        self.error_counts: Dict[str, int] = {}
    
    def record_execution(self, agent_name: str, duration: float, success: bool):
        """실행 기록"""
        if agent_name not in self.execution_stats:
            self.execution_stats[agent_name] = []
            self.error_counts[agent_name] = 0
        
        self.execution_stats[agent_name].append(duration)
        
        if not success:
            self.error_counts[agent_name] += 1
    
    def get_stats(self, agent_name: str) -> Dict[str, Any]:
        """Agent별 통계"""
        if agent_name not in self.execution_stats:
            return {}
        
        durations = self.execution_stats[agent_name]
        
        return {
            "total_executions": len(durations),
            "average_duration": sum(durations) / len(durations),
            "min_duration": min(durations),
            "max_duration": max(durations),
            "error_count": self.error_counts[agent_name],
            "success_rate": 1.0 - (self.error_counts[agent_name] / len(durations))
        }

# 전역 모니터 인스턴스
agent_monitor = AgentMonitor()