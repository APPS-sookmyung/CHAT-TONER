"""공통 API 의존성"""

from typing import Optional, Annotated
from fastapi import Depends, HTTPException, Header
from dependency_injector.wiring import inject, Provide

from core.container import Container

from services.user_service import UserService

from services.vector_store_pg import VectorStorePG





async def get_current_user_optional(

    x_user_id: Annotated[Optional[str], Header()] = None

) -> Optional[dict]:

    """선택적 사용자 인증"""

    if not x_user_id:

        return None

    

    # 실제 사용자 검증 로직

    return {"user_id": x_user_id}



@inject

async def get_user_service(

    user_service: Annotated[

        UserService,

        Depends(Provide[Container.user_service])

    ]

) -> UserService:

    """사용자 서비스 의존성"""

    return user_service





async def get_vector_store() -> VectorStorePG:

    """벡터 저장소 의존성"""

    try:

        store = await VectorStorePG.from_enterprise_db()

        return store

    except Exception as e:

        # 로깅 추가 권장

        print(f"Vector store connection failed: {e}")

        raise HTTPException(status_code=500, detail="Internal server error")
