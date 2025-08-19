# database.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 1. os에서 환경 변수(DATABASE_URL)를 불러옵니다.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./chat_toner.db")

# 2. create_engine을 사용해 데이터베이스 엔진을 생성합니다.
# connect_args는 SQLite를 사용할 때만 필요한 옵션이지만, 포함해두는 경우가 많습니다.
engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True, 
    connect_args={"check_same_thread": False}
)

# 3. 데이터베이스와 통신할 세션(Session)을 관리하는 클래스를 만듭니다.
# autoflush=False, autocommit=False는 세션을 자동으로 커밋하지 않도록 설정하는 표준적인 옵션입니다.
SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

# 4. SQLAlchemy 모델들이 상속할 기본 클래스를 만듭니다.
# 나중에 models.py 파일에서 만들 모든 DB 테이블 모델들은 이 Base를 상속받게 됩니다.
Base = declarative_base()

# 5. FastAPI에서 사용할 DB 세션 의존성 함수 (선택)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()