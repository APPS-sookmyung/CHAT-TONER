# python_backend/core/config.py
# BaseSettings + .env + @lru_cache 
from pydantic_settings import BaseSettings
import os
from functools import lru_cache
from pydantic import Field
from typing import Optional
from pathlib import Path

class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    PROJECT_NAME: str = "Chat Toner API"
    DESCRIPTION: str = "AI 기반 한국어 텍스트 스타일 개인화 API"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 서버 설정
    HOST: str = "0.0.0.0"
    # HOST: str = "127.0.0.1"
    # PORT: int = 5001
    PORT: int = int(os.environ.get("PORT", 8080))
    
    # OpenAI 설정
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"
    
    # 데이터베이스 설정
    DATABASE_URL: Optional[str] = None
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "chattoner"
    DB_USER: str = "chattoner-user"
    DB_PASS: str = ""

    @property
    def POSTGRES_URL(self) -> str:
        """PostgreSQL DATABASE_URL 생성"""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    # CORS 설정
    CORS_ORIGINS: list = ["*"]
    CORS_METHODS: list = ["*"]
    CORS_HEADERS: list = ["*"]
    
    # 피드백 보안키 설정
    SECRET_KEY: str = "default-secret-key-for-dev"

    # 애플리케이션 기본 경로 (개발/배포 환경 분리)
    # 로컬 개발 시에는 프로젝트 루트, 배포 시에는 /app 등으로 설정
    APP_BASE_PATH: Path = Path(os.getenv("APP_BASE_PATH", Path(__file__).resolve().parents[2]))

    class Config:
        env_file = Path(__file__).resolve().parent.parent / ".env"  # 프로젝트 루트의 .env 파일 참조
        case_sensitive = True
        extra = "ignore"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()