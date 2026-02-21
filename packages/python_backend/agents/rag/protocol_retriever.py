"""
Protocol Retriever - FAISS 기반 회사 가이드라인 검색
vector_db.py의 기능을 활용하여 저장된 인덱스 로드 및 검색
"""

from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# 절대 경로 사용
_CURRENT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _CURRENT_DIR.parent.parent  # packages/python_backend
PDF_DIR = _PROJECT_ROOT / "langchain_pipeline" / "data" / "documents"
FAISS_INDEX_DIR = _PROJECT_ROOT / "langchain_pipeline" / "data" / "faiss_index"


class ProtocolRetriever:
    """
    PDF 프로토콜 문서 → FAISS 벡터 인덱스 → 청크 검색

    우선순위:
    1. 저장된 FAISS 인덱스 로드 (빠름)
    2. 없으면 PDF에서 새로 생성 후 저장
    """

    def __init__(self, top_k: int = 3):
        self.top_k = top_k
        self._default_index = None  # 기본 인덱스 (company_id 없을 때)
        self._company_indexes: dict = {}  # company_id → FAISS index
        self._available = False
        self._embeddings = None

    def initialize(self):
        """서버 시작 시 FAISS 인덱스 로드"""
        try:
            from langchain_community.vectorstores import FAISS
            from langchain_openai import OpenAIEmbeddings
            import os

            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.error("[Retriever] OPENAI_API_KEY 없음 → fallback 모드")
                return

            self._embeddings = OpenAIEmbeddings(
                api_key=api_key,
                model="text-embedding-3-small",
            )

            # 1. 기본 인덱스 로드 시도
            if self._load_saved_index():
                self._available = True
                return

            # 2. 저장된 인덱스 없으면 PDF에서 새로 생성
            if self._build_index_from_pdf():
                self._available = True
                return

            logger.warning("[Retriever] 인덱스 로드/생성 실패 → fallback 모드")

        except Exception as e:
            logger.error(f"[Retriever] 초기화 실패: {e} → fallback 모드")
            self._available = False

    def _load_saved_index(self) -> bool:
        """저장된 FAISS 인덱스 로드"""
        from langchain_community.vectorstores import FAISS

        try:
            # 기본 인덱스 로드
            default_index_path = FAISS_INDEX_DIR
            if default_index_path.exists() and (default_index_path / "index.faiss").exists():
                self._default_index = FAISS.load_local(
                    str(default_index_path),
                    self._embeddings,
                    allow_dangerous_deserialization=True
                )
                logger.info(f"[Retriever] 기본 인덱스 로드: {self._default_index.index.ntotal}개 벡터")

            # 회사별 인덱스 로드
            for company_dir in FAISS_INDEX_DIR.iterdir():
                if company_dir.is_dir() and (company_dir / "index.faiss").exists():
                    company_id = company_dir.name
                    self._company_indexes[company_id] = FAISS.load_local(
                        str(company_dir),
                        self._embeddings,
                        allow_dangerous_deserialization=True
                    )
                    logger.info(f"[Retriever] 회사 인덱스 로드: {company_id}")

            return self._default_index is not None or len(self._company_indexes) > 0

        except Exception as e:
            logger.warning(f"[Retriever] 저장된 인덱스 로드 실패: {e}")
            return False

    def _build_index_from_pdf(self) -> bool:
        """PDF에서 FAISS 인덱스 생성 및 저장"""
        from langchain_community.vectorstores import FAISS
        from langchain_community.document_loaders import PyPDFLoader
        from langchain.text_splitter import RecursiveCharacterTextSplitter

        try:
            if not PDF_DIR.exists():
                logger.warning(f"[Retriever] PDF 디렉토리 없음: {PDF_DIR}")
                return False

            pdf_files = list(PDF_DIR.glob("*.pdf"))
            if not pdf_files:
                logger.warning("[Retriever] PDF 파일 없음")
                return False

            splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50,
            )

            all_chunks = []
            for pdf_path in pdf_files:
                company_id = pdf_path.stem
                logger.info(f"[Retriever] PDF 처리 중: {pdf_path.name}")

                loader = PyPDFLoader(str(pdf_path))
                docs = loader.load()
                chunks = splitter.split_documents(docs)

                for chunk in chunks:
                    chunk.metadata["company_id"] = company_id
                    chunk.metadata["company_name"] = company_id
                    chunk.metadata["source"] = pdf_path.name

                all_chunks.extend(chunks)
                logger.info(f"[Retriever] {company_id}: {len(chunks)}개 청크")

            if not all_chunks:
                return False

            # 통합 인덱스 생성 및 저장
            self._default_index = FAISS.from_documents(all_chunks, self._embeddings)

            FAISS_INDEX_DIR.mkdir(parents=True, exist_ok=True)
            self._default_index.save_local(str(FAISS_INDEX_DIR))

            logger.info(f"[Retriever]인덱스 생성 및 저장 완료: {len(all_chunks)}개 청크")
            return True

        except Exception as e:
            logger.error(f"[Retriever] PDF 인덱스 생성 실패: {e}")
            return False

    async def search(
        self,
        query: str,
        company_id: Optional[str] = None,
    ) -> tuple[list[str] | None, str | None]:
        """
        유사 문서 검색

        Args:
            query: 검색 쿼리
            company_id: 회사 ID (있으면 해당 회사 인덱스 우선)

        Returns:
            (chunks, company_name) | (None, None)
        """
        if not self._available:
            return None, None

        try:
            index = None
            name = None

            # 회사별 인덱스 우선
            if company_id and company_id in self._company_indexes:
                index = self._company_indexes[company_id]
                name = company_id
            elif self._default_index:
                index = self._default_index
                name = "default"
            elif self._company_indexes:
                # 회사 인덱스 중 첫 번째 사용
                name = next(iter(self._company_indexes))
                index = self._company_indexes[name]

            if not index:
                return None, None

            # 검색 수행
            results = index.similarity_search(query, k=self.top_k)

            if not results:
                return None, None

            chunks = [doc.page_content for doc in results]

            # 메타데이터에서 실제 company_name 추출
            if results[0].metadata.get("company_name"):
                name = results[0].metadata["company_name"]

            logger.info(f"[Retriever] 검색 완료: {len(chunks)}개 청크 (source: {name})")
            return chunks, name

        except Exception as e:
            logger.error(f"[Retriever] 검색 실패: {e}")
            return None, None

    def get_status(self) -> dict:
        """RAG 상태 확인"""
        return {
            "available": self._available,
            "default_index_loaded": self._default_index is not None,
            "default_index_vectors": self._default_index.index.ntotal if self._default_index else 0,
            "company_indexes": list(self._company_indexes.keys()),
            "pdf_dir": str(PDF_DIR),
            "faiss_index_dir": str(FAISS_INDEX_DIR),
        }