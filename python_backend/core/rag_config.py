"""
RAG 공통 설정
단일 테넌트(stand-alone) 환경을 기본으로 하는 최소 설정 모듈
"""

from __future__ import annotations

import os
import logging
from functools import lru_cache
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class RAGConfig:
    """RAG 관련 경로/모델/청킹 설정을 제공"""

    # 단일 회사(stand-alone) 기준 고정 경로
    faiss_index_path: Path = Path("/tmp/langchain_pipeline/data/faiss_index")
    documents_path: Path = Path("/tmp/langchain_pipeline/data/documents")

    # 임베딩/청킹 설정
    _embedding_model: str = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
    _chunk_size: int = int(os.getenv("RAG_CHUNK_SIZE", "1000"))
    _chunk_overlap: int = int(os.getenv("RAG_CHUNK_OVERLAP", "200"))

    def validate(self) -> None:
        """기본 경로 및 키 점검(치명적 오류는 발생시키지 않음)"""
        try:
            # 경로 존재 확인(없으면 이후 ingest 시 생성)
            if not self.documents_path.exists():
                logger.info(f"문서 경로가 아직 없습니다: {self.documents_path}")
            if not self.faiss_index_path.exists():
                logger.info(f"FAISS 인덱스 경로가 아직 없습니다: {self.faiss_index_path}")

            api_key = self.get_openai_api_key()
            if not api_key:
                logger.warning("OPENAI_API_KEY가 설정되지 않았습니다")
        except Exception as e:
            logger.warning(f"RAG 설정 검증 중 경고: {e}")

    def get_embedding_model(self) -> str:
        return self._embedding_model

    def get_chunk_size(self) -> int:
        return self._chunk_size

    def get_chunk_overlap(self) -> int:
        return self._chunk_overlap

    @lru_cache(maxsize=1)
    def get_openai_api_key(self) -> Optional[str]:
        """OpenAI API 키를 환경에서 조회(없으면 None)"""
        from core.config import get_settings
        settings = get_settings()
        api_key = getattr(settings, "OPENAI_API_KEY", "") or None
        if api_key and api_key.startswith("sk-"):
            return api_key
        return None


@lru_cache(maxsize=1)
def get_rag_config() -> RAGConfig:
    cfg = RAGConfig()
    cfg.validate()
    return cfg

