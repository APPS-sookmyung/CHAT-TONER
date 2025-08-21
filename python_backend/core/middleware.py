"""
FastAPI 미들웨어 설정
CORS, 로깅, 에러 핸들링 등의 미들웨어 구성
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import json
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# 새로 추가될 로깅 미들웨어 함수
async def log_requests_middleware(request: Request, call_next):
    """
    API 요청 및 응답 본문을 로깅하는 미들웨어
    """
    logger = logging.getLogger("api.access")
    
    # --- 요청 정보 로깅 ---
    logger.info(f"Request: {request.method} {request.url}")
    
    # --- 응답 처리 ---
    response = await call_next(request)
    
    # 응답 본문을 읽기 위해 스트림을 소비합니다.
    response_body = b""
    async for chunk in response.body_iterator:
        response_body += chunk
    
    # --- 응답 정보 로깅 ---
    log_message = f"Response: {response.status_code}"
    try:
        # 응답 본문이 JSON 형태이면 예쁘게 출력합니다.
        response_json = json.loads(response_body)
        log_message += f"\n{json.dumps(response_json, indent=2, ensure_ascii=False)}"
    except (json.JSONDecodeError, UnicodeDecodeError):
        # JSON이 아니면 텍스트로 출력합니다.
        log_message += f" Body: {response_body.decode(errors='ignore')}"

    logger.info(log_message)

    # 스트림을 소비했으므로, 동일한 내용으로 새로운 응답을 만들어 반환해야 합니다.
    return Response(
        content=response_body,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type
    )


def setup_middleware(app: FastAPI, settings):
    """미들웨어 설정"""
    
    # CORS 미들웨어
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # --- 로깅 설정 (수정된 부분) ---
    if settings.DEBUG:
        # "api.access" 로거를 직접 설정하여 uvicorn의 로거와 분리합니다.
        logger = logging.getLogger("api.access")
        logger.setLevel(logging.INFO)
        
        # 핸들러 및 포맷터 설정
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        # 중복 로깅을 방지하기 위해 기존 핸들러를 제거하고 새로 추가합니다.
        if logger.hasHandlers():
            logger.handlers.clear()
        logger.addHandler(handler)
        
        # 루트 로거로의 전파를 막아 독립적으로 동작하도록 합니다.
        logger.propagate = False

    # 디버그 모드일 때만 로깅 미들웨어 추가
    if settings.DEBUG:
        app.add_middleware(BaseHTTPMiddleware, dispatch=log_requests_middleware)
