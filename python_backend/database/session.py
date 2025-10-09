from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from core.config import settings

# 비동기 엔진 생성
engine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)

# 비동기 세션 생성
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# API 요청마다 DB 세션을 생성하고 닫는 의존성
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session