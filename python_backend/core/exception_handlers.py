"""
FastAPI 예외 핸들러 설정
전역 예외 처리 및 에러 응답 포맷팅
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
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
        """요청 검증 예외 핸들러"""
        def serialize_error_details(errors):
            """에러 세부사항을 JSON 직렬화 가능하도록 변환"""
            serializable_errors = []
            for error in errors:
                serializable_error = {}
                for key, value in error.items():
                    if isinstance(value, bytes):
                        serializable_error[key] = f"<bytes data: {len(value)} bytes>"
                    elif hasattr(value, '__dict__'):
                        serializable_error[key] = str(value)
                    else:
                        serializable_error[key] = value
                serializable_errors.append(serializable_error)
            return serializable_errors

        return JSONResponse(
            status_code=422,
            content={
                "error": "Validation Error",
                "details": serialize_error_details(exc.errors())
            }
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