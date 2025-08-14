"""공통 API 의존성"""

from typing import Optional, Annotated
from fastapi import Depends, HTTPException, Header

async def get_current_user_optional(
    x_user_id: Annotated[Optional[str], Header()] = None
) -> Optional[dict]:
    """선택적 사용자 인증"""
    if not x_user_id:
        return None
    
    # 실제 사용자 검증 로직
    return {"user_id": x_user_id}

