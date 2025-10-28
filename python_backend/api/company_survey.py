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
    company_id는 문자열 키로 받아 조회합니다.
    """
    # 1) company_id는 문자열 키이므로 company_id 컬럼으로 조회
    profile = (
        db.query(CompanyProfile)
        .filter(CompanyProfile.company_id == company_id)
        .first()
    )

    if profile is None:
        # 2) 스키마 필드명과 DB 컬럼 정확히 매핑
        profile = CompanyProfile(
            company_id=company_id,
            company_name=payload.company_name,
            team_size=payload.team_size,
            communication_style=payload.communication_style,
            main_channels=[payload.main_channel],     # 단일 → 리스트로 저장
            target_audience=payload.main_target,
            survey_data=payload.model_dump(),  # 기존 호환성
            updated_at=datetime.utcnow(),
        )
        db.add(profile)
    else:
        # 업데이트 경로
        profile.company_name = payload.company_name
        profile.team_size = payload.team_size
        profile.communication_style = payload.communication_style
        profile.main_channels = [payload.main_channel]
        profile.target_audience = payload.main_target
        profile.survey_data = payload.model_dump()  # 기존 호환성
        profile.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(profile)
    return {
        "company_id": profile.company_id,
        "company_name": profile.company_name,
        "team_size": profile.team_size,
        "communication_style": profile.communication_style,
        "main_channels": profile.main_channels,
        "target_audience": profile.target_audience,
        "id": profile.id,
    }