"""
Simple Text Embedder (OpenAI API 없이)
한국어 텍스트 임베딩을 위한 간단한 구현
TF-IDF와 코사인 유사도를 사용한 문서 검색
"""

import os
import pickle
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from collections import Counter
import math
import re

logger = logging.getLogger(__name__)

class SimpleTextEmbedder:
    """OpenAI 없이 동작하는 간단한 텍스트 임베딩 시스템"""
    
    def __init__(self, save_path: Path = None):
        """
        초기화
        
        Args:
            save_path: 임베딩 인덱스 저장 경로
        """
        self.save_path = save_path or Path("langchain_pipeline/data/simple_embeddings")
        self.save_path.mkdir(parents=True, exist_ok=True)
        
        # 문서 저장소
        self.documents = []  # 원본 문서들
        self.doc_vectors = []  # 문서 벡터들
        self.vocabulary = {}  # 단어-인덱스 매핑
        self.idf_scores = {}  # IDF 점수
        
        # 한국어 불용어 리스트
        self.stopwords = {
            '을', '를', '이', '가', '은', '는', '의', '에', '와', '과', '으로', '로',
            '에서', '까지', '부터', '보다', '처럼', '같이', '하지만', '그러나', '그리고',
            '또한', '그래서', '따라서', '하다', '있다', '없다', '되다', '이다', '아니다'
        }
    
    def _tokenize(self, text: str) -> List[str]:
        """텍스트를 토큰으로 분할"""
        # 한국어 특성에 맞는 간단한 토큰화
        # 공백과 구두점으로 분할
        text = re.sub(r'[^\w\s]', ' ', text)
        tokens = text.split()
        
        # 불용어 제거 및 길이 필터링
        tokens = [token.lower() for token in tokens 
                 if token not in self.stopwords and len(token) > 1]
        
        return tokens
    
    def _build_vocabulary(self, documents: List[str]):
        """어휘집 구축"""
        all_tokens = []
        for doc in documents:
            tokens = self._tokenize(doc)
            all_tokens.extend(tokens)
        
        # 최소 빈도 필터링 (2회 이상 출현)
        token_counts = Counter(all_tokens)
        filtered_tokens = [token for token, count in token_counts.items() if count >= 2]
        
        # 어휘집 생성
        self.vocabulary = {token: idx for idx, token in enumerate(set(filtered_tokens))}
        logger.info(f"어휘집 크기: {len(self.vocabulary)}")
    
    def _calculate_tf_idf(self, documents: List[str]):
        """TF-IDF 벡터 계산"""
        doc_count = len(documents)
        
        # IDF 계산
        doc_freq = Counter()
        for doc in documents:
            tokens = set(self._tokenize(doc))
            for token in tokens:
                if token in self.vocabulary:
                    doc_freq[token] += 1
        
        self.idf_scores = {}
        for token in self.vocabulary:
            df = doc_freq.get(token, 0)
            if df > 0:
                self.idf_scores[token] = math.log(doc_count / df)
            else:
                self.idf_scores[token] = 0
        
        # 각 문서의 TF-IDF 벡터 계산
        self.doc_vectors = []
        for doc in documents:
            tokens = self._tokenize(doc)
            token_counts = Counter(tokens)
            
            # TF-IDF 벡터 생성
            vector = [0.0] * len(self.vocabulary)
            for token, count in token_counts.items():
                if token in self.vocabulary:
                    tf = count / len(tokens) if tokens else 0
                    idf = self.idf_scores.get(token, 0)
                    vector[self.vocabulary[token]] = tf * idf
            
            # 벡터 정규화
            norm = math.sqrt(sum(x * x for x in vector))
            if norm > 0:
                vector = [x / norm for x in vector]
            
            self.doc_vectors.append(vector)
    
    def fit(self, documents: List[str]) -> bool:
        """문서들로 임베딩 모델 학습"""
        try:
            logger.info(f"임베딩 학습 시작: {len(documents)}개 문서")
            
            self.documents = documents.copy()
            
            # 어휘집 구축
            self._build_vocabulary(documents)
            
            # TF-IDF 계산
            self._calculate_tf_idf(documents)
            
            logger.info("임베딩 학습 완료")
            return True
            
        except Exception as e:
            logger.error(f"임베딩 학습 실패: {e}")
            return False
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """코사인 유사도 계산"""
        if len(vec1) != len(vec2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def _text_to_vector(self, text: str) -> List[float]:
        """텍스트를 벡터로 변환"""
        tokens = self._tokenize(text)
        token_counts = Counter(tokens)
        
        # TF-IDF 벡터 생성
        vector = [0.0] * len(self.vocabulary)
        for token, count in token_counts.items():
            if token in self.vocabulary:
                tf = count / len(tokens) if tokens else 0
                idf = self.idf_scores.get(token, 0)
                vector[self.vocabulary[token]] = tf * idf
        
        # 벡터 정규화
        norm = math.sqrt(sum(x * x for x in vector))
        if norm > 0:
            vector = [x / norm for x in vector]
        
        return vector
    
    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """쿼리와 유사한 문서 검색"""
        if not self.documents:
            logger.warning("학습된 문서가 없습니다")
            return []
        
        try:
            # 쿼리를 벡터로 변환
            query_vector = self._text_to_vector(query)
            
            # 각 문서와의 유사도 계산
            similarities = []
            for i, doc_vector in enumerate(self.doc_vectors):
                similarity = self._cosine_similarity(query_vector, doc_vector)
                similarities.append((self.documents[i], similarity))
            
            # 유사도 순으로 정렬
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"검색 실패: {e}")
            return []
    
    def save(self) -> bool:
        """임베딩 모델 저장"""
        try:
            save_file = self.save_path / "simple_embeddings.pkl"
            
            data = {
                'documents': self.documents,
                'doc_vectors': self.doc_vectors,
                'vocabulary': self.vocabulary,
                'idf_scores': self.idf_scores
            }
            
            with open(save_file, 'wb') as f:
                pickle.dump(data, f)
            
            logger.info(f"임베딩 모델 저장됨: {save_file}")
            return True
            
        except Exception as e:
            logger.error(f"모델 저장 실패: {e}")
            return False
    
    def load(self) -> bool:
        """저장된 임베딩 모델 로드"""
        try:
            save_file = self.save_path / "simple_embeddings.pkl"
            
            if not save_file.exists():
                logger.info("저장된 모델이 없습니다")
                return False
            
            with open(save_file, 'rb') as f:
                data = pickle.load(f)
            
            self.documents = data['documents']
            self.doc_vectors = data['doc_vectors']
            self.vocabulary = data['vocabulary']
            self.idf_scores = data['idf_scores']
            
            logger.info(f"임베딩 모델 로드됨: {len(self.documents)}개 문서")
            return True
            
        except Exception as e:
            logger.error(f"모델 로드 실패: {e}")
            return False

def create_embeddings_from_documents(documents_path: Path) -> bool:
    """문서 폴더에서 임베딩 생성"""
    try:
        embedder = SimpleTextEmbedder()
        
        # 기존 모델 로드 시도
        if embedder.load():
            logger.info("기존 임베딩 모델을 사용합니다")
            return True
        
        # 문서 로드
        documents = []
        if documents_path.exists():
            for txt_file in documents_path.glob("*.txt"):
                try:
                    content = txt_file.read_text(encoding='utf-8')
                    documents.append(content)
                    logger.info(f"문서 로드: {txt_file.name}")
                except Exception as e:
                    logger.error(f"문서 로드 실패 {txt_file}: {e}")
        
        if not documents:
            logger.warning("로드할 문서가 없습니다")
            return False
        
        # 임베딩 학습 및 저장
        if embedder.fit(documents):
            return embedder.save()
        
        return False
        
    except Exception as e:
        logger.error(f"임베딩 생성 실패: {e}")
        return False

if __name__ == "__main__":
    # 테스트 코드
    docs_path = Path("langchain_pipeline/data/documents")
    
    if create_embeddings_from_documents(docs_path):
        print("임베딩 생성 성공")
        
        # 검색 테스트
        embedder = SimpleTextEmbedder()
        if embedder.load():
            results = embedder.search("비즈니스 표현", top_k=3)
            print("\nSearch results:")
            for doc, score in results:
                print(f"점수: {score:.3f} | 문서: {doc[:50]}...")
    else:
        print("임베딩 생성 실패")