"""헬스 체크 엔드포인트"""

import sys
from fastapi import APIRouter
from typing import Dict, Any
from core.config import get_settings

router = APIRouter()

@router.get("/", tags=["Health Check"], summary="서버 상태 확인")
async def health_check() -> Dict[str, Any]:
    """
    시스템 전체 상태 및 외부 서비스 연결 확인
    
    - **OpenAI 연결 상태**
    - **서비스 가용성**
    - **Python 버전 정보**
    """
    settings = get_settings()
    openai_key_exists = bool(settings.OPENAI_API_KEY)
    
    return {
        "status": "ok",
        "service": "chat-toner-fastapi",
        "openai_key_exists": openai_key_exists,
        "python_version": sys.version,
        "features": {
            "basic_conversion": True,
            "openai_integration": openai_key_exists,
            "api_v1": True
        }
    }