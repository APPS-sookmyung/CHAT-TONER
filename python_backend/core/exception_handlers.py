"""
FastAPI 예외 핸들러 설정
전역 예외 처리 및 에러 응답 포맷팅
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
import logging

logger = logging.getLogger(__name__)


def setup_exception_handlers(app: FastAPI):
    """예외 핸들러 설정"""
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """HTTP 예외 핸들러"""
        print(f"[EXCEPTION] HTTP Exception: {exc.status_code} - {exc.detail}")
        print(f"[EXCEPTION] Request URL: {request.url}")
        logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail} for {request.url}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.detail,
                "status_code": exc.status_code
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """요청 검증 예외 핸들러 - jsonable_encoder 사용"""
        # bytes -> "<N bytes>"로 안전 변환
        details = jsonable_encoder(
            exc.errors(),
            custom_encoder={
                bytes: lambda b: f"<{len(b)} bytes>"
            },
        )
        return JSONResponse(
            status_code=422,
            content={"error": "Validation Error", "details": details},
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """일반 예외 핸들러"""
        logger.error(f"Unhandled exception: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred"
            }
        )