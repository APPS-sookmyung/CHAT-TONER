"""
Performance Cache Module
API 성능 최적화를 위한 캐싱 시스템
"""

import functools
import hashlib
import json
import time
from typing import Any, Callable, Dict, Optional
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

class PerformanceCache:
    """메모리 기반 성능 캐시"""

    def __init__(self, max_size: int = 1000, ttl_seconds: int = 300):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds

    def _generate_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """캐시 키 생성"""
        key_data = {
            'func': func_name,
            'args': str(args),
            'kwargs': sorted(kwargs.items())
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()

    def _is_expired(self, timestamp: float) -> bool:
        """캐시 만료 확인"""
        return time.time() - timestamp > self.ttl_seconds

    def get(self, key: str) -> Optional[Any]:
        """캐시에서 값 조회"""
        if key in self.cache:
            cache_entry = self.cache[key]
            if not self._is_expired(cache_entry['timestamp']):
                logger.debug(f"캐시 히트: {key[:16]}...")
                return cache_entry['value']
            else:
                # 만료된 캐시 제거
                del self.cache[key]
                logger.debug(f"캐시 만료 제거: {key[:16]}...")
        return None

    def set(self, key: str, value: Any) -> None:
        """캐시에 값 저장"""
        # 캐시 크기 제한
        if len(self.cache) >= self.max_size:
            # 가장 오래된 항목 제거
            oldest_key = min(self.cache.keys(),
                           key=lambda k: self.cache[k]['timestamp'])
            del self.cache[oldest_key]
            logger.debug(f"캐시 크기 제한으로 제거: {oldest_key[:16]}...")

        self.cache[key] = {
            'value': value,
            'timestamp': time.time()
        }
        logger.debug(f"캐시 저장: {key[:16]}...")

    def clear(self) -> None:
        """캐시 전체 삭제"""
        self.cache.clear()
        logger.info("캐시 전체 삭제")

# 글로벌 캐시 인스턴스
_performance_cache = PerformanceCache()

def cached_api_call(ttl_seconds: int = 300):
    """API 호출 결과 캐싱 데코레이터"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = _performance_cache._generate_key(func.__name__, args, kwargs)

            # 캐시에서 조회
            cached_result = _performance_cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # 캐시 미스 - 실제 함수 실행
            start_time = time.time()
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time

            # 결과 캐싱 (5초 이상 걸린 호출만)
            if execution_time > 5.0:
                _performance_cache.set(cache_key, result)
                logger.info(f"느린 API 호출 캐싱: {func.__name__} ({execution_time:.2f}s)")

            return result
        return wrapper
    return decorator

# RAG 서비스 결과 캐싱
@lru_cache(maxsize=100)
def cached_rag_embedding(text: str, model: str = "text-embedding-3-small") -> str:
    """RAG 임베딩 결과 캐싱 (동일 텍스트 재처리 방지)"""
    # 실제 임베딩은 RAG 서비스에서 처리
    # 여기서는 캐시 키만 생성
    return hashlib.md5(f"{text}:{model}".encode()).hexdigest()

def clear_performance_cache():
    """성능 캐시 초기화"""
    _performance_cache.clear()
    cached_rag_embedding.cache_clear()
    logger.info("모든 성능 캐시 초기화 완료")

def get_cache_stats() -> Dict[str, Any]:
    """캐시 통계 반환"""
    return {
        "total_entries": len(_performance_cache.cache),
        "max_size": _performance_cache.max_size,
        "ttl_seconds": _performance_cache.ttl_seconds,
        "rag_cache_info": cached_rag_embedding.cache_info()._asdict()
    }