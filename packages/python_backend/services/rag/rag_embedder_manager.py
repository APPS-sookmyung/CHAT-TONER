"""
RAG Embedder Manager
임베더 초기화 및 관리를 담당하는 모듈
"""

import logging
from typing import Optional, Any
from pathlib import Path
from core.rag_config import get_rag_config

logger = logging.getLogger('chattoner.rag.embedder')


class RAGEmbedderManager:
    """임베더 초기화 및 생명주기 관리"""
    
    def __init__(self):
        """임베더 매니저 초기화"""
        self.simple_embedder: Optional[Any] = None
        self._initialize_embedder()
    
    def _initialize_embedder(self):
        """GPT Embedder 초기화 (Simple Embedder 폴백 제거)"""
        # @@ [윤지원] 기업 특화 임베딩 부족: 기업별 지식베이스, 가이드라인 문서 처리 로직 없음

        # GPT Embedder 필수: 실패 시 예외 발생
        if not self._try_gpt_embedder():
            error_msg = (
                "Failed to initialize GPT Embedder. "
                "Please ensure OPENAI_API_KEY is set and documents are available."
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def _try_gpt_embedder(self) -> bool:
        """GPT Embedder 초기화 시도"""
        try:
            from langchain_pipeline.embedder.gpt_embedder import GPTTextEmbedder
            gpt_embedder = GPTTextEmbedder()
            
            if not gpt_embedder.is_available():
                logger.warning("OpenAI API 사용 불가 - Simple Embedder로 전환")
                return False
            
            # 기존 임베딩 로드 시도
            if gpt_embedder.load():
                logger.info("GPT Text Embedder 로드 완료")
                self.simple_embedder = gpt_embedder
                return True
            
            # 새로 생성
            documents = self._load_documents()
            if documents and gpt_embedder.fit(documents) and gpt_embedder.save():
                logger.info("GPT 임베딩 생성 및 저장 완료")
                self.simple_embedder = gpt_embedder
                return True
                
            logger.warning("GPT 임베딩 생성 실패")
            return False
            
        except Exception as e:
            logger.warning(f"GPT Embedder 초기화 실패: {e}")
            return False
    
    def _load_documents(self) -> list:
        """문서 로드 공통 함수"""
        cfg = get_rag_config()
        docs_path = Path(cfg.documents_path)
        documents = []
        
        if not docs_path.exists():
            logger.warning(f"문서 폴더가 존재하지 않음: {docs_path}")
            return documents
        
        for txt_file in docs_path.glob("*.txt"):
            try:
                content = txt_file.read_text(encoding='utf-8')
                if content.strip():  # 빈 파일 제외
                    documents.append(content)
            except Exception as e:
                logger.warning(f"문서 로드 실패 {txt_file}: {e}")
                
        logger.info(f"총 {len(documents)}개 문서 로드됨")
        return documents
    
    def get_embedder(self) -> Optional[Any]:
        """현재 활성화된 임베더 반환"""
        return self.simple_embedder
    
    def is_available(self) -> bool:
        """임베더 사용 가능 여부"""
        return self.simple_embedder is not None
