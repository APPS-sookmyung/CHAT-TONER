"""
LangChain Pipeline - Retriever Module

이 모듈은 문서 검색 및 벡터 데이터베이스 관련 기능을 제공합니다.

주요 구성요소:
- vector_db: FAISS 벡터 저장소 생성 및 관리
- doc_splitter: 문서 청크 분할 기능
"""

from .vector_db import (
    ingest_documents_from_folder,
    get_embedding,
    FAISS_INDEX_PATH,
    DOCUMENTS_PATH
)

from .doc_splitter import split_documents, get_text_splitter

__all__ = [
    "ingest_documents_from_folder",
    "get_embedding", 
    "split_documents",
    "get_text_splitter",
    "FAISS_INDEX_PATH",
    "DOCUMENTS_PATH"
]