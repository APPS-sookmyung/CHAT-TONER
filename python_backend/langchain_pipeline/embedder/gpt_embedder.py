"""
GPT Embeddings를 사용한 텍스트 임베딩 시스템
OpenAI text-embedding-3-small 모델 활용
"""

import os
import pickle
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
import numpy as np
from openai import OpenAI
from core.config import get_settings
settings = get_settings()

logger = logging.getLogger(__name__)

class GPTTextEmbedder:
    """OpenAI GPT Embeddings를 사용한 텍스트 임베딩 시스템"""
    
    def __init__(self, save_path: Optional[Path] = None):
        """초기화"""
        self.save_path = save_path or Path("langchain_pipeline/data/gpt_embeddings")
        self.save_path.mkdir(parents=True, exist_ok=True)
        
        self.client = None
        self.model = "text-embedding-3-small"
        self.embedding_dimension = 1536
        
        self.documents = []
        self.doc_embeddings = []
        
        self._initialize_client()
    
    def _initialize_client(self):
        """OpenAI 클라이언트 초기화"""
        try:
            # .env 파일에서 API 키 로드
            dotenv_path = Path(__file__).resolve().parents[3] / ".env"
            if dotenv_path.exists():
                from dotenv import load_dotenv
                load_dotenv(dotenv_path=dotenv_path)
            
            from core.config import get_settings
            settings = get_settings()
        except Exception as e:
            logger.error(f"OpenAI 클라이언트 초기화 실패: {e}")
            return
    api_key = settings.OPENAI_API_KEY

    def _get_embedding(self, text: str) -> Optional[List[float]]:
        """텍스트의 GPT 임베딩 생성"""
        if not self.client:
            return None
        
        try:
            if len(text) > 8000:
                text = text[:8000]
            
            response = self.client.embeddings.create(
                model=self.model,
                input=text,
                encoding_format="float"
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"임베딩 생성 실패: {e}")
            return None
    
    def fit(self, documents: List[str]) -> bool:
        """문서들로 임베딩 모델 학습"""
        try:
            logger.info(f"GPT 임베딩 생성 시작: {len(documents)}개 문서")
            
            if not self.client:
                return False
            
            self.documents = documents.copy()
            self.doc_embeddings = []
            
            for i, doc in enumerate(documents):
                embedding = self._get_embedding(doc)
                if embedding is None:
                    return False
                
                self.doc_embeddings.append(embedding)
            
            logger.info("GPT 임베딩 생성 완료")
            return True
            
        except Exception as e:
            logger.error(f"임베딩 학습 실패: {e}")
            return False
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """코사인 유사도 계산"""
        try:
            a = np.array(vec1)
            b = np.array(vec2)
            
            dot_product = np.dot(a, b)
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)
            
            if norm_a == 0 or norm_b == 0:
                return 0.0
            
            return dot_product / (norm_a * norm_b)
            
        except Exception as e:
            logger.error(f"유사도 계산 실패: {e}")
            return 0.0
    
    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """쿼리와 유사한 문서 검색"""
        if not self.documents or not self.doc_embeddings:
            return []
        
        try:
            query_embedding = self._get_embedding(query)
            if query_embedding is None:
                return []
            
            similarities = []
            for i, doc_embedding in enumerate(self.doc_embeddings):
                similarity = self._cosine_similarity(query_embedding, doc_embedding)
                similarities.append((self.documents[i], similarity))
            
            similarities.sort(key=lambda x: x[1], reverse=True)
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"검색 실패: {e}")
            return []
    
    def save(self) -> bool:
        """임베딩 모델 저장"""
        try:
            save_file = self.save_path / "gpt_embeddings.pkl"
            
            data = {
                'documents': self.documents,
                'doc_embeddings': self.doc_embeddings,
                'model': self.model,
                'embedding_dimension': self.embedding_dimension
            }
            
            with open(save_file, 'wb') as f:
                pickle.dump(data, f)
            
            logger.info(f"GPT 임베딩 모델 저장됨: {save_file}")
            return True
            
        except Exception as e:
            logger.error(f"모델 저장 실패: {e}")
            return False
    
    def load(self) -> bool:
        """저장된 임베딩 모델 로드"""
        try:
            save_file = self.save_path / "gpt_embeddings.pkl"
            
            if not save_file.exists():
                return False
            
            with open(save_file, 'rb') as f:
                data = pickle.load(f)
            
            self.documents = data['documents']
            self.doc_embeddings = data['doc_embeddings']
            self.model = data.get('model', self.model)
            self.embedding_dimension = data.get('embedding_dimension', self.embedding_dimension)
            
            logger.info(f"GPT 임베딩 모델 로드됨: {len(self.documents)}개 문서")
            return True
            
        except Exception as e:
            logger.error(f"모델 로드 실패: {e}")
            return False
    
    def is_available(self) -> bool:
        """OpenAI API 사용 가능 여부 확인"""
        return self.client is not None
    
    def get_stats(self) -> Dict[str, Any]:
        """임베딩 시스템 통계 정보"""
        return {
            "model": self.model,
            "dimension": self.embedding_dimension,
            "document_count": len(self.documents),
            "api_available": self.is_available()
        }