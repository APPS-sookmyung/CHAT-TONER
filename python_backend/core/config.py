# python_backend/core/config.py
# BaseSettings + .env + @lru_cache 
from pydantic_settings import BaseSettings
import os
from functools import lru_cache

class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    PROJECT_NAME: str = "Chat Toner API"
    DESCRIPTION: str = "AI 기반 한국어 텍스트 스타일 개인화 API"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 서버 설정
    HOST: str = "0.0.0.0"
    PORT: int = 5001
    
    # OpenAI 설정
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"
    
    # 데이터베이스 설정
    DATABASE_URL: str = "sqlite:///./chat_toner.db"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "chattoner_db"
    DB_USER: str = "username"
    DB_PASSWORD: str = "password"
    
    # CORS 설정
    CORS_ORIGINS: list = ["*"]
    CORS_METHODS: list = ["*"]
    CORS_HEADERS: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()