"""
1. fastapi 인스턴스 생성 
2. cors 설정 
3. 라우터 등록
4. 루트 health 체크 엔드포인트
5. uvicorn 실행
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.conversion_routes import router as conversation_router
from services.conversion_service import ConversionService
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from datetime import datetime
#from schemas import __version__


dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=dotenv_path)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성 함수 분리
def create_app() -> FastAPI:
    app = FastAPI(
        title="Chat Toner API",
        description="AI 기반 텍스트 스타일 변환 서비스",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )
    return app
# FastAPI 앱 인스턴스 생성
app = create_app()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발용
    allow_methods=["*"],
    allow_headers=["*"],
)

# 기존 라우터 등록

app.include_router(conversation_router, prefix="/api/conversation", tags=["대화"])


# 루트 엔드포인트
@app.get("/")
async def root():
    return {"message": "Chat Toner API", "docs": "/docs"}

# 정적 파일 서빙 (선택사항)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)