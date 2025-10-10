from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import create_access_token # 토큰 생성 함수
from services.user_service import UserService
from db.session import get_db # DB 세션 의존성 import
from core.container import Container
from dependency_injector.wiring import inject, Provide
from passlib.context import CryptContext

router = APIRouter()

@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)] # DB 세션을 주입받습니다.
):
    # UserService를 통해 사용자를 인증합니다.
    user_service = UserService(db)
    user = await user_service.authenticate(
        username=form_data.username, password=form_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token = create_access_token(
        data={"sub": user.id}
    )
    return {"access_token": access_token, "token_type": "bearer"}