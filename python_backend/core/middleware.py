"""
FastAPI 미들웨어 설정
CORS, 로깅, 에러 핸들링, 성능 최적화 등의 미들웨어 구성
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import logging
import json
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class PerformanceMiddleware(BaseHTTPMiddleware):
    """API 성능 모니터링 미들웨어"""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # 요청 정보 로깅
        logger = logging.getLogger("api.access")
        logger.debug(f"요청 시작: {request.method} {request.url.path}")

        try:
            response = await call_next(request)

            # 성능 측정
            process_time = time.time() - start_time

            # 응답 헤더에 성능 정보 추가
            response.headers["X-Process-Time"] = str(process_time)

            # 항상 기본 액세스 로그 1줄 출력 (메소드, 경로, 상태코드, 처리시간)
            logger.info(
                f"{request.method} {request.url.path} -> {getattr(response, 'status_code', 'NA')} "
                f"({process_time:.3f}s)"
            )

            # 추가 성능 로깅 (임계치 기반)
            if process_time > 5.0:
                logger.warning(f"느린 API 호출: {request.method} {request.url.path} - {process_time:.2f}s")
            elif process_time > 2.0:
                logger.info(f"보통 API 호출: {request.method} {request.url.path} - {process_time:.2f}s")
            else:
                logger.debug(f"빠른 API 호출: {request.method} {request.url.path} - {process_time:.2f}s")

            return response

        except Exception as e:
            process_time = time.time() - start_time
            logger.error(f"API 오류 ({process_time:.2f}s): {request.method} {request.url.path} - {str(e)}")
            raise

# 기존 로깅 미들웨어 함수 (유지)
async def log_requests_middleware(request: Request, call_next):
    """
    API 요청 및 응답 본문을 로깅하는 미들웨어 (디버그 모드에서만)
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
    """미들웨어 설정 - 성능 최적화 포함"""

    # 1. 성능 모니터링 미들웨어 (가장 바깥쪽)
    app.add_middleware(PerformanceMiddleware)

    # 2. GZIP 압축 미들웨어 (응답 크기 감소로 네트워크 성능 향상)
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # 3. CORS 미들웨어
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- 로깅 설정 ---
    # "api.access" 로거를 uvicorn과 별도로 stdout으로 항상 설정
    access_logger = logging.getLogger("api.access")
    if not access_logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        access_logger.addHandler(handler)
    # 기본 레벨은 INFO (환경에 따라 DEBUG로 조정)
    access_logger.setLevel(logging.DEBUG if getattr(settings, 'DEBUG', False) else logging.INFO)
    access_logger.propagate = False

    # 디버그 모드일 때만 상세 로깅 미들웨어 추가 (요청/응답 본문)
    if settings.DEBUG:
        app.add_middleware(BaseHTTPMiddleware, dispatch=log_requests_middleware)

    logging.getLogger("chattoner").info("성능 최적화 미들웨어 설정 완료")
