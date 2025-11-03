from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, conint
from database.db import get_db
from database.models import CompanyProfile

router = APIRouter(prefix="/surveys", tags=["surveys"])

class CompanySurveyRequest(BaseModel):
    communication_style: str
    company_name: str
    main_channel: str                 # 단일 문자열
    main_target: List[str] = Field(default_factory=list)  # 리스트
    team_size: conint(ge=1)

@router.post("/company/{company_id}")
def submit_company_survey(company_id: str, payload: CompanySurveyRequest, db: Session = Depends(get_db)):
    """
    기업용 설문조사를 제출받아 처리하고, 해당 기업의 프로필을 업데이트하는 엔드포인트입니다.
    """
    try:
        company_id_int = int(company_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="company_id must be a valid integer")

    # company_id로 CompanyProfile 조회 또는 생성
    company_profile = db.query(CompanyProfile).filter(CompanyProfile.id == company_id_int).first()
    
    if not company_profile:
        company_profile = CompanyProfile(id=company_id_int, company_name=payload.company_name)
        db.add(company_profile)

    # 설문 데이터로 프로필 업데이트
    company_profile.team_size = payload.team_size
    company_profile.main_channel = payload.main_channel
    company_profile.main_target = payload.main_target
    company_profile.communication_style = payload.communication_style
    company_profile.survey_data = payload.dict()
    company_profile.updated_at = datetime.utcnow()

    try:
        db.commit()
        db.refresh(company_profile)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred while updating the profile: {e}")

    return {
        "message": "Company survey submitted and profile updated successfully.",
        "company_profile": {
            "id": company_profile.id,
            "company_name": company_profile.company_name,
            "team_size": company_profile.team_size,
            "main_channel": company_profile.main_channel,
            "main_target": company_profile.main_target,
            "communication_style": company_profile.communication_style,
            "updated_at": company_profile.updated_at.isoformat()
        }
    }
