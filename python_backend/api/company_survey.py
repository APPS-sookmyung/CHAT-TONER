from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel, Field, conint
from database.db import get_db
from database.models import CompanyProfile

router = APIRouter(prefix="/api/v1/surveys", tags=["surveys"])

class CompanySurveyRequest(BaseModel):
    communication_style: str
    company_name: str
    main_channel: str                 # 단일 문자열
    main_target: list[str] = Field(default_factory=list)  # 리스트
    team_size: conint(ge=1)

@router.post("/company/{company_id}")
def submit_company_survey(company_id: str, payload: CompanySurveyRequest, db: Session = Depends(get_db)):
    """
    기업용 설문조사를 제출받아 처리하는 엔드포인트입니다.
    company_id를 정수로 변환해서 기존 id 컬럼과 비교합니다.
    """
    try:
        # company_id를 정수로 변환
        company_id_int = int(company_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="company_id must be a valid integer")

    # 기존 id 컬럼으로 조회
    profile = (
        db.query(CompanyProfile)
        .filter(CompanyProfile.id == company_id_int)
        .first()
    )

    if profile is None:
        # 새 프로필 생성 - id는 자동 증가이므로 설정하지 않음
        profile = CompanyProfile(
            company_name=payload.company_name,
            survey_data=payload.model_dump(),
            updated_at=datetime.utcnow(),
        )
        db.add(profile)
    else:
        # 기존 프로필 업데이트
        profile.company_name = payload.company_name
        profile.survey_data = payload.model_dump()
        profile.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(profile)
    return {
        "company_id": profile.id,  # integer id 반환
        "company_name": profile.company_name,
        "survey_data": profile.survey_data,
        "id": profile.id,
    }