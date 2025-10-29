"""
FAISS 벡터 데이터베이스 관리
문서 임베딩, 저장, 검색 기능 제공
# @@ @rosaze 기업별 분리 부족:  모든 기업이 동일한 FAISS 인덱스 공유, 기업별 지식베이스 격리 필요
"""

import logging
import os
import sys
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any

# 프로젝트 루트 경로 설정
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

# LangChain imports
try:
    from langchain_community.vectorstores import FAISS, PGVector
    from langchain_community.document_loaders import TextLoader, PyPDFLoader
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_openai import OpenAIEmbeddings
    from langchain.schema import Document
    from dotenv import load_dotenv
    from core.config import get_settings
    
    # PGVector settings
    db_settings = get_settings()
    CONNECTION_STRING = db_settings.POSTGRES_URL
    COLLECTION_NAME = "chattoner_embeddings"
    except ImportError as e:
    logging.error(f"LangChain 라이브러리 import 실패: {e}")
    raise

# 로거 설정
logger = logging.getLogger(__name__)

# 설정 (공통 설정에서 가져옴)


def get_embedding():
    """OpenAI 임베딩 인스턴스 반환 (공통 설정 사용)"""
    from core.rag_config import get_rag_config

    config = get_rag_config()
    api_key = config.get_openai_api_key()

    if not api_key:
        raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다")

    return OpenAIEmbeddings(
        model=config.get_embedding_model(),
        api_key=api_key
    )

def get_vector_store() -> PGVector:
    """PGVector 스토어 인스턴스를 반환합니다."""
    embeddings = get_embedding()
    store = PGVector(
        connection_string=CONNECTION_STRING,
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME,
    )
    return store


def load_documents_from_folder(folder_path: Path) -> List[Document]:
    """폴더에서 문서 로드"""
    documents = []
    
    if not folder_path.exists():
        logger.warning(f"문서 폴더가 존재하지 않음: {folder_path}")
        return documents
    
    # .txt 파일 로드
    for txt_file in folder_path.glob("*.txt"):
        try:
            with open(txt_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if content.strip():
                doc = Document(
                    page_content=content,
                    metadata={"source": str(txt_file.name)}
                )
                documents.append(doc)
                logger.info(f"텍스트 파일 로드: {txt_file.name}")
                
        except Exception as e:
            logger.error(f"텍스트 파일 로드 실패 {txt_file}: {e}")
    
    # .pdf 파일 로드 (있는 경우)
    for pdf_file in folder_path.glob("*.pdf"):
        try:
            loader = PyPDFLoader(str(pdf_file))
            pdf_docs = loader.load()
            
            for doc in pdf_docs:
                doc.metadata["source"] = pdf_file.name
            
            documents.extend(pdf_docs)
            logger.info(f"PDF 파일 로드: {pdf_file.name} ({len(pdf_docs)}페이지)")
            
        except Exception as e:
            logger.error(f"PDF 파일 로드 실패 {pdf_file}: {e}")
    
    logger.info(f"총 {len(documents)}개 문서 로드됨")
    return documents

def split_documents(documents: List[Document]) -> List[Document]:
    """문서를 청크로 분할"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        separators=["\n\n", "\n", ".", "!", "?", " ", ""]
    )
    
    split_docs = text_splitter.split_documents(documents)
    logger.info(f"문서 분할 완료: {len(documents)}개 → {len(split_docs)}개 청크")
    
    return split_docs



def ingest_documents_from_folder(folder_path: Path, save_path: Optional[Path] = None) -> Tuple[Optional[PGVector], List[Document]]:
    """
    폴더에서 문서를 로드하고 PGVector에 저장합니다.

    Args:
        folder_path: 문서가 있는 폴더 경로

    Returns:
        (벡터저장소, 원본문서리스트) 튜플
    """
    try:
        logger.info(f"문서 인덱싱 시작: {folder_path}")

        # 1. 문서 로드
        documents = load_documents_from_folder(folder_path)
        if not documents:
            logger.warning("로드된 문서가 없습니다")
            return None, []

        # 2. 문서 분할
        split_docs = split_documents(documents)

        # 3. PGVector 스토어 가져오기
        vectorstore = get_vector_store()

        # 4. 문서 추가
        vectorstore.add_documents(split_docs)
        logger.info(f"PGVector에 {len(split_docs)}개 청크 추가 완료")

        # 5. PostgreSQL에 메타데이터 저장
        _save_document_metadata_to_postgres(folder_path, documents, split_docs, vectorstore)

        logger.info("문서 인덱싱 완료")
        return vectorstore, documents

    except Exception as e:
        logger.exception(f"문서 인덱싱 실패: {e}")
        return None, []

def _save_document_metadata_to_postgres(folder_path: Path, documents: List[Document],
                                       split_docs: List[Document], vectorstore: PGVector):
    """PostgreSQL에 벡터 문서 메타데이터 저장"""
    try:
        from core.container import Container
        from core.rag_config import get_rag_config

        config = get_rag_config()
        storage = Container.database_storage()

        for doc in documents:
            file_path = doc.metadata.get("source", "unknown")
            file_path_obj = folder_path / file_path if not Path(file_path).is_absolute() else Path(file_path)

            if file_path_obj.exists():
                file_size = file_path_obj.stat().st_size

                # 메타데이터 구성
                metadata = {
                    "file_name": file_path_obj.name,
                    "file_path": str(file_path_obj),
                    "file_size_bytes": file_size,
                    "content_type": _get_content_type(file_path_obj),
                    "embedding_model": config.get_embedding_model(),
                    "chunk_count": len([d for d in split_docs if d.metadata.get("source") == file_path]),
                    "chunk_size": config.get_chunk_size(),
                    "chunk_overlap": config.get_chunk_overlap(),
                    "vector_db_collection": COLLECTION_NAME,
                    "vector_dimension": len(vectorstore.embedding_function.embed_query("test")),
                    "status": "active"
                }

                success = storage.save_vector_document_metadata(metadata)
                if success:
                    logger.info(f"문서 메타데이터 저장 완료: {file_path_obj.name}")
                else:
                    logger.warning(f"문서 메타데이터 저장 실패: {file_path_obj.name}")

    except Exception as e:
        logger.error(f"PostgreSQL 메타데이터 저장 중 오류: {e}")

def _get_content_type(file_path: Path) -> str:
    """파일 확장자에 따른 컨텐츠 타입 반환"""
    suffix = file_path.suffix.lower()
    content_types = {
        ".txt": "text/plain",
        ".pdf": "application/pdf",
        ".md": "text/markdown",
        ".doc": "application/msword",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    }
    return content_types.get(suffix, "text/plain")

def search_similar_documents(query: str, top_k: int = 5) -> List[Tuple[Document, float]]:
    """유사한 문서 검색"""
    try:
        vectorstore = get_vector_store()
        if not vectorstore:
            logger.warning("벡터 저장소가 로드되지 않았습니다")
            return []
        
        # 유사도 검색
        results = vectorstore.similarity_search_with_score(query, k=top_k)
        
        logger.info(f"검색 완료: {len(results)}개 결과")
        return results
        
    except Exception as e:
        logger.exception(f"문서 검색 실패: {e}")
        return []

def get_vector_store_stats() -> Dict[str, Any]:
    """벡터 저장소 통계 정보"""
    try:
        vectorstore = get_vector_store()
        # Test the connection by embedding a dummy query
        vectorstore.embedding_function.embed_query("test")
        
        return {
            "status": "ready",
            "document_count": "N/A",
            "vector_db_collection": COLLECTION_NAME
        }
        
    except Exception as e:
        logger.exception(f"통계 조회 실패: {e}")
        return {
            "status": "error",
            "error": str(e),
            "document_count": 0
        }
