"""
Document Splitter Utilities
텍스트 청킹 및 분할 유틸리티 (구조만 생성)
"""

from typing import List, Dict, Any
from abc import ABC, abstractmethod

class DocumentSplitter(ABC):
    """문서 분할기 추상 클래스"""
    
    @abstractmethod
    def split_text(self, text: str) -> List[str]:
        """텍스트 분할"""
        pass


class RecursiveCharacterSplitter(DocumentSplitter):
    """
    재귀적 문자 기반 텍스트 분할기
    TODO: 실제 LangChain RecursiveCharacterTextSplitter 연동
    """
    
    def __init__(self, 
                 chunk_size: int = 1000,
                 chunk_overlap: int = 200,
                 separators: List[str] = None):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", " ", ""]
    
    def split_text(self, text: str) -> List[str]:
        """텍스트를 청크로 분할 - 향후 구현"""
        # TODO: LangChain RecursiveCharacterTextSplitter 로직 구현
        
        # 임시 간단한 분할 로직 (실제로는 LangChain 사용 예정)
        chunks = []
        current_chunk = ""
        sentences = text.split(". ")
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < self.chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks


class KoreanTextSplitter(DocumentSplitter):
    """
    한국어 특화 텍스트 분할기
    한국어 문장 구조를 고려한 최적화된 분할
    """
    
    def __init__(self, 
                 chunk_size: int = 800,  # 한국어는 다소 작게
                 chunk_overlap: int = 150):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.korean_separators = ["다.", "요.", "습니다.", "였다.", "\n\n", "\n"]
    
    def split_text(self, text: str) -> List[str]:
        """한국어 텍스트 분할 - 향후 구현"""
        # TODO: 한국어 문장 패턴을 고려한 스마트 분할 로직
        
        chunks = []
        sentences = self._split_korean_sentences(text)
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < self.chunk_size:
                current_chunk += sentence + " "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + " "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _split_korean_sentences(self, text: str) -> List[str]:
        """한국어 문장 분리 - 향후 정교화"""
        # TODO: KoNLPy나 다른 한국어 NLP 라이브러리 활용
        import re
        
        # 간단한 한국어 문장 분리 패턴
        pattern = r'[.!?](?=\s|$)'
        sentences = re.split(pattern, text)
        return [s.strip() for s in sentences if s.strip()]


class DocumentChunker:
    """문서 청킹 관리 클래스"""
    
    def __init__(self, splitter_type: str = "korean"):
        self.splitter = self._create_splitter(splitter_type)
    
    def _create_splitter(self, splitter_type: str) -> DocumentSplitter:
        """분할기 타입에 따른 인스턴스 생성"""
        if splitter_type == "korean":
            return KoreanTextSplitter()
        elif splitter_type == "recursive":
            return RecursiveCharacterSplitter()
        else:
            raise ValueError(f"지원하지 않는 분할기 타입: {splitter_type}")
    
    def chunk_documents(self, documents: List[str]) -> List[Dict[str, Any]]:
        """
        문서 목록을 청크로 분할
        
        Args:
            documents: 원본 문서 리스트
            
        Returns:
            청크와 메타데이터가 포함된 딕셔너리 리스트
        """
        chunked_docs = []
        
        for doc_idx, document in enumerate(documents):
            chunks = self.splitter.split_text(document)
            
            for chunk_idx, chunk in enumerate(chunks):
                chunked_docs.append({
                    "content": chunk,
                    "metadata": {
                        "doc_id": f"doc_{doc_idx}",
                        "chunk_id": f"chunk_{chunk_idx}",
                        "chunk_index": chunk_idx,
                        "total_chunks": len(chunks)
                    }
                })
        
        return chunked_docs