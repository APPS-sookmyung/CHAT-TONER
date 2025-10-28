"""공통 API 의존성"""

from typing import Optional, Annotated
from fastapi import Depends, HTTPException, Header
from core.container import Container
from services.conversion_service import ConversionService
from services.document_service import DocumentService

async def get_current_user_optional(
    x_user_id: Annotated[Optional[str], Header()] = None
) -> Optional[dict]:
    """선택적 사용자 인증"""
    if not x_user_id:
        return None
    
    # 실제 사용자 검증 로직
    return {"user_id": x_user_id}

# @@ TODO: 실제 사용자 인증 로직 구현 필요 (JWT 토큰 검증 등)
def get_conversion_service() -> ConversionService:
    """ConversionService 인스턴스를 제공합니다."""
    from fastapi import Request
    from starlette.requests import Request as StarletteRequest

    # FastAPI app에서 container 인스턴스를 가져오기
    # 현재 요청에서 app 인스턴스에 접근하기 어려우므로,
    # Container 인스턴스를 직접 생성해서 사용
    container = Container()
    # 설정을 로드해야 함
    from core.config import get_settings
    settings = get_settings()
    container.config.from_dict(settings.model_dump())
    container.wire(modules=["api.v1.endpoints.conversion"])
    return container.conversion_service()

def get_document_service() -> DocumentService:
    """DocumentService 인스턴스를 제공합니다."""
    container = Container()
    from core.config import get_settings
    settings = get_settings()
    container.config.from_dict(settings.model_dump())
    container.wire(modules=["api.v1.endpoints.documents"])
    return container.document_service()

def get_user_preferences_service():
    """UserPreferencesService 인스턴스를 제공합니다."""
    from services.user_preferences import UserPreferencesService
    container = Container()
    from core.config import get_settings
    settings = get_settings()
    container.config.from_dict(settings.model_dump())
    container.wire(modules=["api.v1.endpoints.profile"])
    return container.user_preferences_service()
