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
    
    #파인 튜닝 추론 서버 설정
    FINETUNE_INFERENCE_HOST: str = Field(default="localhost", validation_alias="RUNPOD_IP")
    FINETUNE_INFERENCE_PORT: int = 8010
    FINETUNE_URL_OVERRIDE: Optional[str] = Field(default=None)

    @property
    def FINETUNE_URL(self) -> str:
        if self.FINETUNE_URL_OVERRIDE:
            return self.FINETUNE_URL_OVERRIDE
        return f"http://{self.FINETUNE_INFERENCE_HOST}:{self.FINETUNE_INFERENCE_PORT}"
    
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

    class Config:
        env_file = Path(__file__).resolve().parent.parent / ".env"  # 프로젝트 루트의 .env 파일 참조
        case_sensitive = True
        extra = "ignore"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()