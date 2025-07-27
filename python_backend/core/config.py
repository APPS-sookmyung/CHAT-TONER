# python_backend/core/config.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Chat Toner"
    openai_api_key: str
    environment: str = "dev"

    class Config:
        env_file = ".env"

settings = Settings()
# python_backend/main.py
