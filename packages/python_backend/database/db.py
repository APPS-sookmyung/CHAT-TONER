from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import get_settings

settings = get_settings()

# PostgreSQL 연결을 위한 설정
database_url = settings.POSTGRES_URL

# SQLite의 경우에만 check_same_thread 사용
connect_args = {}
if database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    database_url,
    connect_args=connect_args,
    pool_pre_ping=True,  # 연결 상태 확인
    pool_recycle=3600    # 1시간마다 연결 재사용
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()