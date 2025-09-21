"""
RAG 관련 공통 설정 관리
환경 설정의 일관성을 보장하고 중복을 제거
"""

import os
import logging
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from functools import lru_cache

logger = logging.getLogger(__name__)

class RAGConfig:
    """RAG 서비스 전용 설정 관리자"""

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._load_environment()
            self._setup_paths()
            self._validate_config()
            self.__class__._initialized = True

    def _load_environment(self):
        """환경 변수 로드 (프로젝트 루트 기준)"""
        try:
            # 프로젝트 루트에서 .env 파일 찾기
            current_file = Path(__file__).resolve()

            # python_backend/core/rag_config.py에서 시작
            project_root = current_file.parents[2]  # 2025-CHATTONER-Server

            # 여러 가능한 .env 위치 확인
            env_locations = [
                project_root / "python_backend" / ".env",
                project_root / ".env",
                Path("python_backend/.env"),
                Path(".env")
            ]

            env_loaded = False
            for env_path in env_locations:
                if env_path.exists():
                    load_dotenv(dotenv_path=env_path)
                    logger.info(f"환경 설정 로드됨: {env_path}")
                    env_loaded = True
                    break

            if not env_loaded:
                logger.warning("환경 설정 파일을 찾을 수 없습니다")

        except Exception as e:
            logger.error(f"환경 설정 로드 실패: {e}")

    def _setup_paths(self):
        """경로 설정"""
        try:
            # 프로젝트 루트 경로
            self.project_root = Path(__file__).resolve().parents[2]

            # RAG 관련 경로들
            self.faiss_index_path = self.project_root / "python_backend/langchain_pipeline/data/faiss_index"
            self.documents_path = self.project_root / "python_backend/langchain_pipeline/data/documents"

            # 디렉토리 생성
            self.faiss_index_path.mkdir(parents=True, exist_ok=True)
            self.documents_path.mkdir(parents=True, exist_ok=True)

        except Exception as e:
            logger.error(f"경로 설정 실패: {e}")
            raise

    def _validate_config(self):
        """설정 검증"""
        try:
            # OpenAI API 키 검증
            api_key = self.get_openai_api_key()
            if not api_key:
                logger.warning("OpenAI API 키가 설정되지 않았습니다")
            elif len(api_key) < 20:
                logger.warning("OpenAI API 키가 너무 짧습니다")
            else:
                logger.info("OpenAI API 키 검증 완료")

            # 경로 접근 권한 검증
            if not self.faiss_index_path.exists():
                logger.warning(f"FAISS 인덱스 경로가 존재하지 않습니다: {self.faiss_index_path}")

            if not self.documents_path.exists():
                logger.warning(f"문서 경로가 존재하지 않습니다: {self.documents_path}")

        except Exception as e:
            logger.error(f"설정 검증 실패: {e}")

    @lru_cache(maxsize=1)
    def get_openai_api_key(self) -> Optional[str]:
        """OpenAI API 키 반환 (캐시됨)"""
        # 여러 소스에서 API 키 확인
        api_key = (
            os.getenv("OPENAI_API_KEY") or
            os.getenv("OPENAI_API_KEY_RAG") or
            None
        )

        if api_key and api_key.startswith("sk-"):
            return api_key

        logger.warning("유효한 OpenAI API 키를 찾을 수 없습니다")
        return None

    def get_database_url(self) -> str:
        """데이터베이스 URL 반환"""
        return os.getenv("DATABASE_URL", "postgresql://postgres:geenie@localhost:5432/chat_toner_db")

    def get_embedding_model(self) -> str:
        """임베딩 모델 이름 반환"""
        return os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

    def get_max_file_size_mb(self) -> int:
        """최대 파일 크기 (MB) 반환"""
        try:
            return int(os.getenv("MAX_FAISS_FILE_SIZE_MB", "500"))
        except ValueError:
            return 500

    def is_debug_mode(self) -> bool:
        """디버그 모드 여부"""
        return os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")

    def get_chunk_size(self) -> int:
        """문서 청크 크기"""
        try:
            return int(os.getenv("RAG_CHUNK_SIZE", "1000"))
        except ValueError:
            return 1000

    def get_chunk_overlap(self) -> int:
        """문서 청크 오버랩"""
        try:
            return int(os.getenv("RAG_CHUNK_OVERLAP", "200"))
        except ValueError:
            return 200

# 싱글톤 인스턴스
@lru_cache(maxsize=1)
def get_rag_config() -> RAGConfig:
    """RAG 설정 싱글톤 인스턴스 반환"""
    return RAGConfig()

def validate_openai_connection() -> bool:
    """OpenAI 연결 테스트"""
    try:
        config = get_rag_config()
        api_key = config.get_openai_api_key()

        if not api_key:
            return False

        # OpenAI 클라이언트로 간단한 테스트
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        # 모델 목록 요청으로 연결 테스트
        models = client.models.list()
        if models:
            logger.info("OpenAI 연결 테스트 성공")
            return True

    except Exception as e:
        logger.error(f"OpenAI 연결 테스트 실패: {e}")

    return False