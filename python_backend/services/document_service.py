
"""
Document Service
기업별 문서 업로드, 처리, 임베딩 및 벡터 DB 저장을 담당하는 서비스
"""
import logging
from pathlib import Path
from typing import List, Dict, Any
import pypdf
from langchain_text_splitters import RecursiveCharacterTextSplitter

# LangChain 구성요소 임포트 (프로젝트 구조에 따라 경로 조정 필요)
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings # 또는 다른 임베딩 모델

logger = logging.getLogger('chattoner')

# --- 상수 정의 ---
# 회사별 벡터 DB가 저장될 기본 경로
COMPANY_DATA_ROOT = Path("python_backend/langchain_pipeline/data/company_specific")
# 텍스트 분할 시 청크 크기 및 중복 크기
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

class DocumentService:
    """기업 문서 처리 및 임베딩 서비스"""

    def __init__(self, openai_api_key: str):
        """
        서비스 초기화
        - OpenAI 임베딩 모델을 설정합니다.
        - 텍스트 분할기(Text Splitter)를 설정합니다.
        """
        if not openai_api_key:
            raise ValueError("OpenAI API 키가 필요합니다.")
        
        # 임베딩 모델 초기화
        self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        
        # 텍스트 분할기 초기화
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
        )
        logger.info("DocumentService 초기화 완료: OpenAI Embeddings 사용")

    def _get_company_vector_store_path(self, company_id: str) -> Path:
        """회사 ID를 기반으로 벡터 저장소의 경로를 반환합니다."""
        path = COMPANY_DATA_ROOT / company_id / "faiss_index"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _parse_pdf(self, file_path: Path) -> str:
        """PDF 파일에서 텍스트를 추출합니다."""
        try:
            with open(file_path, "rb") as f:
                pdf_reader = pypdf.PdfReader(f)
                text = "".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())
            logger.info(f"PDF 파일 파싱 완료: {file_path.name}, {len(text)} 자 추출")
            return text
        except Exception as e:
            logger.error(f"PDF 파일 파싱 중 오류 발생 ({file_path.name}): {e}")
            raise ValueError(f"PDF 파일 처리 실패: {file_path.name}") from e

    def _chunk_text(self, text: str) -> List[str]:
        """주어진 텍스트를 설정된 크기의 청크로 분할합니다."""
        chunks = self.text_splitter.split_text(text)
        logger.info(f"{len(chunks)}개의 텍스트 청크 생성 완료")
        return chunks

    async def process_and_embed_document(self, file_path: Path, company_id: str, document_id: str) -> Dict[str, Any]:
        """
        단일 문서를 처리하고 임베딩하여 회사별 벡터 저장소에 추가(또는 업데이트)합니다.

        Args:
            file_path (Path): 처리할 문서의 경로.
            company_id (str): 문서를 소유한 회사의 고유 ID.
            document_id (str): 문서의 고유 ID.

        Returns:
            처리 결과를 담은 딕셔너리.
        """
        logger.info(f"문서 임베딩 시작: company='{company_id}', doc='{document_id}', file='{file_path.name}'")
        
        try:
            # 1. 파일 타입에 따라 텍스트 추출 (현재는 PDF만 지원)
            if file_path.suffix.lower() != ".pdf":
                raise ValueError("현재 PDF 파일만 지원됩니다.")
            
            document_text = self._parse_pdf(file_path)
            if not document_text.strip():
                return {"success": False, "error": "문서에서 텍스트를 추출할 수 없습니다."}

            # 2. 텍스트를 청크로 분할
            text_chunks = self._chunk_text(document_text)

            # 3. 각 청크에 메타데이터 추가
            # 검색 시 어떤 문서의 어떤 부분인지 식별하기 위함
            metadatas = [{
                "company_id": company_id,
                "document_id": document_id,
                "source_file": file_path.name,
                "chunk_index": i
            } for i in range(len(text_chunks))]

            # 4. 회사별 벡터 저장소 경로 확인 및 로드/생성
            vector_store_path = self._get_company_vector_store_path(company_id)
            
            if (vector_store_path / "index.faiss").exists():
                # 기존 저장소가 있으면 로드
                logger.info(f"기존 FAISS 인덱스 로드: {vector_store_path}")
                vector_store = FAISS.load_local(str(vector_store_path), self.embeddings, allow_dangerous_deserialization=True)
                
                # TODO: 동일 document_id를 가진 기존 청크를 삭제하는 로직 필요
                # vector_store.delete(...)
                
                # 새로운 청크 추가
                vector_store.add_texts(texts=text_chunks, metadatas=metadatas)
            else:
                # 없으면 새로 생성
                logger.info(f"새로운 FAISS 인덱스 생성: {vector_store_path}")
                vector_store = await FAISS.afrom_texts(texts=text_chunks, embedding=self.embeddings, metadatas=metadatas)

            # 5. 업데이트된 벡터 저장소 저장
            vector_store.save_local(str(vector_store_path))
            
            logger.info(f"문서 임베딩 및 저장 완료: {len(text_chunks)}개 청크")
            return {
                "success": True,
                "company_id": company_id,
                "document_id": document_id,
                "chunks_processed": len(text_chunks)
            }

        except Exception as e:
            logger.error(f"문서 처리 중 심각한 오류 발생: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
