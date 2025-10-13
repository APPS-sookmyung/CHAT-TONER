"""
1. fastapi 인스턴스 생성 
2. cors 설정 
3. 라우터 등록
4. 루트 health 체크 엔드포인트
5. uvicorn 실행

Chat Toner FastAPI Main Application
간소화된 메인 애플리케이션 엔트리포인트
"""


import logging
logger= logging.getLogger('chattoner')
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.swagger_config import configure_swagger
from core.swagger_config import get_swagger_ui_parameters
from core.config import get_settings
from core.container import Container
from core.middleware import setup_middleware
from core.exception_handlers import setup_exception_handlers
from api.v1.router import api_router
from starlette.middleware.sessions import SessionMiddleware
from api import feedback

FRONT_ORIGINS = [
    "https://client-184664486594.asia-northeast3.run.app",
    "http://localhost:5173",
]

def create_app() -> FastAPI:
    """FastAPI 애플리케이션 팩토리"""
    settings = get_settings()
    
    logger.info(f"OPENAI_MODEL: {settings.OPENAI_MODEL}")
    logger.info(f"DEBUG: {settings.DEBUG}")
    
    # 컨테이너 초기화
    container = Container()
    #container.config.from_dict(settings.dict())
    container.config.from_dict(settings.model_dump())

    # @@ 주의: 전체 모듈 와이어링 시 순환 참조 및 의존성 오류 발생 가능
    # 와이어링 추가 (의존성 문제 있는 모듈 제외)
    container.wire(modules=[
        "api.v1.endpoints.conversion",
        "api.v1.endpoints.health",
        "api.v1.endpoints.profile",
        "api.v1.endpoints.feedback",
        "api.v1.endpoints.rag",
        "api.v1.endpoints.quality",
        "api.v1.endpoints.company"
        # @@ quality와 company는 langgraph/enterprise 의존성 문제로 제외됨. 추가 필요!!!
    ])
    
    # FastAPI 앱 생성
    swagger_params = get_swagger_ui_parameters()
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.DESCRIPTION,
        version=settings.VERSION,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        **swagger_params
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=FRONT_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if settings.DEBUG:
        configure_swagger(app)
    
    # 컨테이너 연결
    app.container = container
    
    # 미들웨어 설정
    setup_middleware(app, settings)

    # 세션 미들웨어 추가 - secret_key .env 설정 파일에서 관리
    # Temporarily disabled - SessionMiddleware requires additional setup
    # app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

    # 예외 핸들러 설정
    setup_exception_handlers(app)
    
    @app.get("/", tags=["Health Check"])
    async def health_check():
        """서비스 상태를 확인하는 기본 엔드포인트"""
        return {"status": "ok", "message": "Welcome to Chat Toner API!"}
    app.include_router(api_router, prefix="/api/v1")
    app.include_router(feedback.router, tags=["Feedback"])
    
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        access_log=settings.DEBUG
    )
