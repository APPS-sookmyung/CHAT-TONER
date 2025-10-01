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
    return Container.conversion_service()

def get_document_service() -> DocumentService:
    """DocumentService 인스턴스를 제공합니다."""
    return Container.document_service()
