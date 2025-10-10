"""공통 API 의존성"""

from typing import Optional, Annotated
from fastapi import Depends, HTTPException, Header
from dependency_injector.wiring import inject, Provide
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from core.config import settings

from core.container import Container
from services.user_service import UserService

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

# 의존성 함수 - JWT 토큰을 추출하기 위한 OAuth2 스키마 정의
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

@inject
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_service: Annotated[
        UserService,
        Depends(Provide[Container.user_service])
    ]
) -> dict:
    """
    JWT 토큰을 검증하고 현재 사용자를 반환합니다. (인증 필수)
    토큰이 없거나 유효하지 않으면 401 Unauthorized 에러를 발생시킵니다.
    """
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 설정 파일의 SECRET_KEY와 ALGORITHM을 사용하여 토큰을 디코딩한다.
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # 데이터베이스에서 실제 사용자 정보를 조회한다.
    user = await user_service.get_user(user_id=user_id)
    if user is None:
        raise credentials_exception
    return user