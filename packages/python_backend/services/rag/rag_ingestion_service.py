"""
RAG Ingestion Service
문서 인덱싱 및 벡터 스토어 생성을 담당하는 모듈
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path
from core.rag_config import get_rag_config

logger = logging.getLogger('chattoner.rag.ingestion')


class RAGIngestionService:
    """문서 인덱싱 및 벡터 스토어 관리"""
    
    def __init__(self, rag_chain=None):
        """
        인덱싱 서비스 초기화
        
        Args:
            rag_chain: RAG Chain 인스턴스 (선택)
        """
        self.rag_chain = rag_chain
    
    def ingest_documents(self, folder_path: str) -> Dict[str, Any]:
        """
        문서 폴더에서 벡터 DB 생성
        
        Args:
            folder_path: 문서가 있는 폴더 경로
            
        Returns:
            처리 결과 딕셔너리
        """
        if not self.rag_chain:
            return {
                "success": False,
                "error": "RAG 서비스가 초기화되지 않았습니다.",
                "documents_processed": 0
            }
        
        try:
            logger.info(f"문서 인덱싱 요청: {folder_path}")
            
            result = self.rag_chain.ingest_documents(folder_path)
            
            if result.get("success"):
                logger.info(f"문서 인덱싱 완료: {result.get('documents_processed', 0)}개 처리")
            else:
                logger.error(f"문서 인덱싱 실패: {result.get('error')}")
            
            return result
            
        except Exception as e:
            logger.exception(f"문서 인덱싱 중 오류: {e!s}")
            return {
                "success": False,
                "error": f"문서 인덱싱 중 서버 오류가 발생했습니다: {e!s}",
                "documents_processed": 0
            }

    def ingest_company_documents(self, company_id: str, folder_path: str) -> Dict[str, Any]:
        """특정 기업용 문서를 인덱싱하여 기업 전용 벡터 스토어로 저장"""
        try:
            from langchain_pipeline.retriever.vector_db import ingest_documents_from_folder
            cfg = get_rag_config()
            company_index_path = Path(cfg.faiss_index_path) / company_id
            company_index_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"기업 인덱싱 요청: company={company_id}, folder={folder_path}, index={company_index_path}")

            vectorstore, docs = ingest_documents_from_folder(Path(folder_path), save_path=company_index_path)
            if vectorstore is not None:
                # 기업 전용 벡터 스토어 재적용(체인 사용 시)
                if self.rag_chain:
                    try:
                        self.rag_chain.vectorstore = vectorstore
                        self.rag_chain.retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
                        self.rag_chain.is_initialized = True
                    except Exception as e:
                        logger.warning(f"RAGChain에 기업 벡터스토어 적용 실패: {e}")
                return {"success": True, "documents_processed": len(docs)}
            return {"success": False, "error": "문서 처리 실패", "documents_processed": 0}
        except Exception as e:
            logger.exception(f"기업 문서 인덱싱 중 오류: {e!s}")
            return {"success": False, "error": f"{e!s}", "documents_processed": 0}
