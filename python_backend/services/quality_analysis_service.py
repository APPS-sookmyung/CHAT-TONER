"""
텍스트 품질 분석 서비스 통합
Agent와 기존 로직을 연결하는 서비스 레이어
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

from agents.quality_analysis_agent import QualityAnalysisAgent, CONTEXT_CONFIGS, ContextType
from services.rag_service import RAGService

logger = logging.getLogger('chattoner.quality_service')

@dataclass
class QualityAnalysisConfig:
    """품질 분석 설정"""
    enable_agent: bool = True
    fallback_enabled: bool = True
    max_suggestions: int = 4
    rag_timeout: float = 30.0
    confidence_threshold: float = 0.6

class QualityAnalysisService:
    """텍스트 품질 분석 통합 서비스"""
    
    def __init__(self, rag_service: RAGService, config: Optional[QualityAnalysisConfig] = None):
        self.rag_service = rag_service
        self.config = config or QualityAnalysisConfig()
        self.agent = QualityAnalysisAgent(rag_service) if self.config.enable_agent else None
        
        logger.info(f"품질 분석 서비스 초기화 - Agent 사용: {self.config.enable_agent}")
    
    async def analyze_text_quality(
        self, 
        text: str, 
        target_audience: str, 
        context: str,
        detailed: bool = False
    ) -> Dict[str, Any]:
        """통합 텍스트 품질 분석"""
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Agent 분석 시도
            if self.agent and self.config.enable_agent:
                result = await self._analyze_with_agent(text, target_audience, context)
                
                # 신뢰도 확인
                if self._is_result_reliable(result):
                    result['processing_time'] = asyncio.get_event_loop().time() - start_time
                    result['method_used'] = 'agent'
                    
                    if detailed:
                        result.update(await self._add_detailed_analysis(result, text))
                    
                    return result
                else:
                    logger.warning("Agent 결과 신뢰도가 낮아 Fallback으로 전환")
            
            # Fallback 분석
            if self.config.fallback_enabled:
                result = await self._analyze_with_fallback(text, target_audience, context)
                result['processing_time'] = asyncio.get_event_loop().time() - start_time
                result['method_used'] = 'fallback'
                
                if detailed:
                    result.update(await self._add_detailed_analysis(result, text))
                
                return result
            
            raise Exception("분석 방법을 사용할 수 없습니다")
            
        except Exception as e:
            logger.error(f"텍스트 품질 분석 실패: {e}")
            
            # 최종 Fallback
            result = self._create_emergency_fallback(text, target_audience, context)
            result['processing_time'] = asyncio.get_event_loop().time() - start_time
            result['method_used'] = 'emergency_fallback'
            result['error'] = str(e)
            
            return result
    
    async def _analyze_with_agent(
        self, 
        text: str, 
        target_audience: str, 
        context: str
    ) -> Dict[str, Any]:
        """Agent를 사용한 분석"""
        
        try:
            # 타임아웃 설정으로 Agent 실행
            result = await asyncio.wait_for(
                self.agent.analyze(text, target_audience, context),
                timeout=self.config.rag_timeout
            )
            
            logger.info(f"Agent 분석 완료 - RAG 소스: {result.get('rag_sources_count', 0)}")
            return result
            
        except asyncio.TimeoutError:
            logger.warning(f"Agent 분석 타임아웃 ({self.config.rag_timeout}초)")
            raise Exception("분석 시간 초과")
        except Exception as e:
            logger.error(f"Agent 분석 실패: {e}")
            raise
    
    async def _analyze_with_fallback(
        self, 
        text: str, 
        target_audience: str, 
        context: str
    ) -> Dict[str, Any]:
        """Fallback 분석 (기존 휴리스틱 방법)"""
        
        logger.info("Fallback 분석 시작")
        
        # 기본 텍스트 분석
        text_stats = self._calculate_text_statistics(text)
        
        # 맥락별 점수 조정
        context_multiplier = self._get_context_multiplier(context)
        
        # 기본 점수 계산
        base_scores = self._calculate_base_scores(text, text_stats)
        
        # 맥락별 조정 적용
        adjusted_scores = {
            'grammar_score': min(100.0, base_scores['grammar'] * context_multiplier),
            'formality_score': min(100.0, base_scores['formality'] * context_multiplier),
            'readability_score': min(100.0, base_scores['readability'] * context_multiplier)
        }
        
        # 기본 제안 생성
        suggestions = self._generate_fallback_suggestions(
            text, target_audience, context, adjusted_scores
        )
        
        return {
            **adjusted_scores,
            'suggestions': suggestions,
            'rag_sources_count': 0,
            'confidence_level': 'low'
        }
    
    def _is_result_reliable(self, result: Dict[str, Any]) -> bool:
        """결과 신뢰도 평가"""
        
        # 에러 -> 신뢰도 낮음
        if result.get('error'):
            return False
        
        # RAG 소스가 부족 -> 신뢰도 낮음
        if result.get('rag_sources_count', 0) < 1:
            return False
        
        # 점수가 비정상적 -> 신뢰도 낮음
        scores = [
            result.get('grammar_score', 0),
            result.get('formality_score', 0),
            result.get('readability_score', 0)
        ]
        
        if any(score < 0 or score > 100 for score in scores):
            return False
        
        # 제안이 없으면 신뢰도 낮음
        if not result.get('suggestions'):
            return False
        
        return True
    
    def _calculate_text_statistics(self, text: str) -> Dict[str, Any]:
        """텍스트 통계 계산"""
        
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        words = text.split()
        characters = len(text.replace(' ', ''))
        
        avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
        avg_word_length = sum(len(word) for word in words) / max(len(words), 1)
        
        return {
            'character_count': len(text),
            'character_count_no_spaces': characters,
            'word_count': len(words),
            'sentence_count': len(sentences),
            'avg_sentence_length': avg_sentence_length,
            'avg_word_length': avg_word_length
        }
    
    def _get_context_multiplier(self, context: str) -> float:
        """맥락별 점수 조정 배율"""
        
        multipliers = {
            '보고서_공문': 0.88,
            '교육': 1.05,
            '일반': 1.00      
        }
        
        return multipliers.get(context, 1.00)
    
    def _calculate_base_scores(self, text: str, stats: Dict[str, Any]) -> Dict[str, float]:
        """기본 점수 계산 (휴리스틱)"""
        
        # 문법 점수 (기본 70점)
        grammar_score = 70.0
        if stats['character_count'] > 100:
            grammar_score += 10.0
        if stats['word_count'] > 10:
            grammar_score += 5.0
        
        # 격식도 점수 (존댓말 검사)
        formality_score = 60.0
        formal_markers = ['습니다', '됩니다', '있습니다', '드립니다']
        if any(marker in text for marker in formal_markers):
            formality_score += 20.0
        
        # 가독성 점수 (문장 길이 기반)
        if stats['avg_sentence_length'] < 20:
            readability_score = 75.0
        else:
            readability_score = max(40.0, 75.0 - (stats['avg_sentence_length'] - 20) * 2)
        
        return {
            'grammar': grammar_score,
            'formality': formality_score,
            'readability': readability_score
        }
    
    def _generate_fallback_suggestions(
        self, 
        text: str, 
        target_audience: str, 
        context: str, 
        scores: Dict[str, float]
    ) -> List[Dict[str, str]]:
        """Fallback 제안 생성"""
        
        suggestions = []
        
        # 점수가 낮은 항목에 대한 제안 생성
        if scores['grammar_score'] < 70:
            suggestions.append({
                'category': '문법',
                'original': '전체 텍스트',
                'suggestion': '문법적으로 더 정확한 표현으로 수정',
                'reason': f'{target_audience} 대상으로 문법적 정확성을 높여주세요'
            })
        
        if scores['formality_score'] < 70:
            context_name = CONTEXT_CONFIGS.get(
                ContextType(context), 
                CONTEXT_CONFIGS[ContextType.GENERAL]
            ).name
            suggestions.append({
                'category': '격식도',
                'original': '전체 텍스트',
                'suggestion': f'{context_name} 맥락에 적합한 격식도로 조정',
                'reason': f'{context_name} 상황에서는 더 적절한 격식도가 필요합니다'
            })
        
        if scores['readability_score'] < 70:
            suggestions.append({
                'category': '가독성',
                'original': '긴 문장들',
                'suggestion': '더 짧고 명확한 문장으로 분할',
                'reason': f'{target_audience}이 이해하기 쉽도록 가독성을 개선해주세요'
            })
        
        # 기본 제안이 없을 경우
        if not suggestions:
            suggestions.append({
                'category': '일반',
                'original': '전체 텍스트',
                'suggestion': '더 명확하고 적절한 표현으로 개선',
                'reason': '전반적인 표현 개선을 통해 품질을 높일 수 있습니다'
            })
        
        return suggestions[:self.config.max_suggestions]
    
    def _create_emergency_fallback(
        self, 
        text: str, 
        target_audience: str, 
        context: str
    ) -> Dict[str, Any]:
        """응급 Fallback (최소한의 기본 응답)"""
        
        return {
            'grammar_score': 65.0,
            'formality_score': 65.0,
            'readability_score': 65.0,
            'suggestions': [{
                'category': '일반',
                'original': '전체 텍스트',
                'suggestion': '시스템 오류로 인해 상세한 분석이 불가합니다',
                'reason': '임시적인 기술적 문제가 발생했습니다. 잠시 후 다시 시도해주세요'
            }],
            'rag_sources_count': 0,
            'confidence_level': 'low'
        }
    
    async def _add_detailed_analysis(
        self, 
        base_result: Dict[str, Any], 
        text: str
    ) -> Dict[str, Any]:
        """상세 분석 정보 추가"""
        
        text_stats = self._calculate_text_statistics(text)
        
        detailed_info = {
            'text_statistics': {
                **text_stats,
                'readability_index': self._calculate_readability_index(text_stats)
            },
            'improvement_priority': self._determine_improvement_priority(base_result),
            'analysis_metadata': {
                'total_suggestions': len(base_result.get('suggestions', [])),
                'confidence_level': base_result.get('confidence_level', 'unknown'),
                'rag_sources_used': base_result.get('rag_sources_count', 0)
            }
        }
        
        return detailed_info
    
    def _calculate_readability_index(self, stats: Dict[str, Any]) -> str:
        """가독성 지수 계산"""
        
        avg_sentence_length = stats.get('avg_sentence_length', 0)
        avg_word_length = stats.get('avg_word_length', 0)
        
        if avg_sentence_length <= 15 and avg_word_length <= 4:
            return "쉬움"
        elif avg_sentence_length <= 25 and avg_word_length <= 6:
            return "보통"
        else:
            return "어려움"
    
    def _determine_improvement_priority(self, result: Dict[str, Any]) -> List[str]:
        """개선 우선순위 결정"""
        
        scores = [
            ("문법", result.get('grammar_score', 70)),
            ("격식도", result.get('formality_score', 70)),
            ("가독성", result.get('readability_score', 70))
        ]
        
        # 낮은 점수순 정렬
        low_scores = [(name, score) for name, score in scores if score < 75]
        low_scores.sort(key=lambda x: x[1])
        
        priorities = [name for name, _ in low_scores]
        
        # 모든 점수가 양호하면 가장 낮은 항목 우선
        if not priorities:
            min_item = min(scores, key=lambda x: x[1])
            priorities.append(min_item[0])
        
        return priorities
    
    async def get_context_suggestions(
        self, 
        text: str, 
        context: str
    ) -> Dict[str, Any]:
        """맥락별 제안 생성"""
        
        try:
            # 맥락 설정 확인
            context_config = None
            for ctx in ContextType:
                if ctx.value == context:
                    context_config = CONTEXT_CONFIGS[ctx]
                    break
            
            if not context_config:
                context_config = CONTEXT_CONFIGS[ContextType.GENERAL]
            
            # RAG를 통한 맥락별 제안 생성
            prompt = self._build_context_suggestions_prompt(context_config, text)
            
            rag_result = await self.rag_service.ask_generative_question(
                query=prompt,
                context=f"{context_config.name} 맥락 제안"
            )
            
            if rag_result and rag_result.get("success"):
                import json
                suggestions_data = json.loads(rag_result["answer"])
                
                # 맥락별 피드백 형태로 변환
                enhanced_suggestions = []
                for sugg in suggestions_data:
                    enhanced_reason = context_config.feedback_template.format(
                        original=sugg.get("original", ""),
                        reason=sugg.get("reason", ""),
                        suggestion=sugg.get("suggestion", "")
                    )
                    
                    enhanced_suggestions.append({
                        'original': sugg.get("original", ""),
                        'suggestion': sugg.get("suggestion", ""),
                        'reason': enhanced_reason,
                        'category': 'context_specific'
                    })
                
                return {
                    'suggestions': enhanced_suggestions,
                    'count': len(enhanced_suggestions),
                    'context_type': context,
                    'method_used': 'rag'
                }
            
        except Exception as e:
            logger.error(f"맥락별 제안 생성 실패: {e}")
        
        # Fallback 제안
        return self._create_fallback_context_suggestions(text, context)
    
    def _build_context_suggestions_prompt(self, context_config, text: str) -> str:
        """맥락별 제안 프롬프트 구성"""
        
        criteria_text = "\n".join([
            f"- {key}: {desc}" 
            for key, desc in context_config.scoring_criteria.items()
        ])
        
        return f"""'{context_config.name}' 맥락의 글쓰기 가이드를 참고하여, 
다음 텍스트에서 개선할 수 있는 표현을 3개 찾아주세요.

{context_config.name} 맥락 특징: {context_config.description}

평가 기준:
{criteria_text}

반드시 JSON 형식으로만 응답:
[
  {{
    "original": "개선 필요한 표현",
    "suggestion": "{context_config.name} 맥락에 적합한 표현",
    "reason": "{context_config.name} 관점에서 개선 이유"
  }}
]

분석할 텍스트:
{text}"""
    
    def _create_fallback_context_suggestions(
        self, 
        text: str, 
        context: str
    ) -> Dict[str, Any]:
        """맥락별 제안 Fallback"""
        
        context_name = CONTEXT_CONFIGS.get(
            ContextType(context), 
            CONTEXT_CONFIGS[ContextType.GENERAL]
        ).name
        
        fallback_suggestions = [{
            'original': '전체 텍스트',
            'suggestion': f'{context_name} 맥락에 더 적합한 표현으로 수정',
            'reason': f'{context_name} 상황의 특성을 고려한 표현 개선이 필요합니다',
            'category': 'context_fallback'
        }]
        
        return {
            'suggestions': fallback_suggestions,
            'count': 1,
            'context_type': context,
            'method_used': 'fallback'
        }

def create_quality_analysis_service(
    rag_service: RAGService,
    enable_agent: bool = True,
    fallback_enabled: bool = True
) -> QualityAnalysisService:
    """품질 분석 서비스 생성"""
    
    config = QualityAnalysisConfig(
        enable_agent=enable_agent,
        fallback_enabled=fallback_enabled,
        max_suggestions=4,
        rag_timeout=30.0,
        confidence_threshold=0.6
    )
    
    return QualityAnalysisService(rag_service, config)

# 성능 모니터링 데코레이터
import functools
import time

def monitor_performance(func):
    """성능 모니터링 데코레이터"""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            logger.info(f"{func.__name__} 실행 완료 - 소요시간: {duration:.2f}초")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"{func.__name__} 실행 실패 - 소요시간: {duration:.2f}초, 오류: {e}")
            raise
    return wrapper