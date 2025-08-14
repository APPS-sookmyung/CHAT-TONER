"""
FAISS 벡터 데이터베이스 관리
문서 임베딩, 저장, 검색 기능 제공
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
    from langchain_community.vectorstores import FAISS
    from langchain_community.document_loaders import TextLoader, PyPDFLoader
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_openai import OpenAIEmbeddings
    from langchain.schema import Document
    from dotenv import load_dotenv
except ImportError as e:
    logging.error(f"LangChain 라이브러리 import 실패: {e}")
    raise

# 로거 설정
logger = logging.getLogger(__name__)

# 설정
FAISS_INDEX_PATH = Path("python_backend/langchain_pipeline/data/faiss_index")
DOCUMENTS_PATH = Path("python_backend/langchain_pipeline/data/documents")

def get_embedding():
    """OpenAI 임베딩 인스턴스 반환"""
    # .env 파일 로드
    dotenv_path = Path(__file__).resolve().parents[3] / ".env"
    load_dotenv(dotenv_path=dotenv_path)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다")
    
    return OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=api_key
    )

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

def create_vector_store(documents: List[Document]) -> FAISS:
    """문서로부터 FAISS 벡터 저장소 생성"""
    try:
        embeddings = get_embedding()
        
        if not documents:
            raise ValueError("임베딩할 문서가 없습니다")
        
        # FAISS 벡터 저장소 생성
        vectorstore = FAISS.from_documents(documents, embeddings)
        logger.info(f"FAISS 벡터 저장소 생성 완료: {len(documents)}개 문서")
        
        return vectorstore
        
    except Exception as e:
        logger.error(f"벡터 저장소 생성 실패: {e}")
        raise

def save_vector_store(vectorstore: FAISS, save_path: Path):
    """벡터 저장소를 파일로 저장"""
    try:
        save_path.mkdir(parents=True, exist_ok=True)
        
        vectorstore.save_local(str(save_path))
        logger.info(f"벡터 저장소 저장됨: {save_path}")
        
    except Exception as e:
        logger.error(f"벡터 저장소 저장 실패: {e}")
        raise

def load_vector_store(load_path: Path) -> Optional[FAISS]:
    """저장된 벡터 저장소 로드"""
    try:
        if not load_path.exists() or not any(load_path.iterdir()):
            logger.warning(f"벡터 저장소가 없음: {load_path}")
            return None
        
        embeddings = get_embedding()
        vectorstore = FAISS.load_local(
            str(load_path), 
            embeddings,
            allow_dangerous_deserialization=True
        )
        
        logger.info(f"벡터 저장소 로드됨: {vectorstore.index.ntotal}개 벡터")
        return vectorstore
        
    except Exception as e:
        logger.error(f"벡터 저장소 로드 실패: {e}")
        return None

def ingest_documents_from_folder(folder_path: Path) -> Tuple[Optional[FAISS], List[Document]]:
    """
    폴더에서 문서를 로드하고 벡터 저장소 생성
    
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
        
        # 3. 벡터 저장소 생성
        vectorstore = create_vector_store(split_docs)
        
        # 4. 저장
        save_vector_store(vectorstore, FAISS_INDEX_PATH)
        
        logger.info("문서 인덱싱 완료")
        return vectorstore, documents
        
    except Exception as e:
        logger.error(f"문서 인덱싱 실패: {e}")
        return None, []

def search_similar_documents(query: str, top_k: int = 5) -> List[Tuple[Document, float]]:
    """유사한 문서 검색"""
    try:
        vectorstore = load_vector_store(FAISS_INDEX_PATH)
        if not vectorstore:
            logger.warning("벡터 저장소가 로드되지 않았습니다")
            return []
        
        # 유사도 검색
        results = vectorstore.similarity_search_with_score(query, k=top_k)
        
        logger.info(f"검색 완료: {len(results)}개 결과")
        return results
        
    except Exception as e:
        logger.error(f"문서 검색 실패: {e}")
        return []

def get_vector_store_stats() -> Dict[str, Any]:
    """벡터 저장소 통계 정보"""
    try:
        vectorstore = load_vector_store(FAISS_INDEX_PATH)
        if not vectorstore:
            return {
                "status": "not_found",
                "document_count": 0,
                "index_path": str(FAISS_INDEX_PATH)
            }
        
        return {
            "status": "ready",
            "document_count": vectorstore.index.ntotal,
            "index_path": str(FAISS_INDEX_PATH),
            "documents_path": str(DOCUMENTS_PATH)
        }
        
    except Exception as e:
        logger.error(f"통계 조회 실패: {e}")
        return {
            "status": "error",
            "error": str(e),
            "document_count": 0
        }

if __name__ == "__main__":
    # 테스트 코드
    print("🔍 FAISS 벡터 데이터베이스 테스트")
    
    # 문서 인덱싱
    vectorstore, docs = ingest_documents_from_folder(DOCUMENTS_PATH)
    
    if vectorstore:
        print(f"✅ 인덱싱 완료: {len(docs)}개 문서")
        
        # 검색 테스트
        test_query = "비즈니스 메일 작성"
        results = search_similar_documents(test_query, top_k=3)
        
        print(f"\n🔍 검색 결과 ('{test_query}'):")
        for i, (doc, score) in enumerate(results, 1):
            print(f"{i}. 점수: {score:.3f}")
            print(f"   내용: {doc.page_content[:100]}...")
            print(f"   출처: {doc.metadata.get('source', 'Unknown')}")
            print()
    else:
        print("❌ 인덱싱 실패")