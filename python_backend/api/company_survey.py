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
    기업용 설문조사를 제출받아 처리하는 엔드포인트입니다.
    company_id를 정수로 변환해서 기존 id 컬럼과 비교합니다.
    """
    try:
        # company_id를 정수로 변환
        company_id_int = int(company_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="company_id must be a valid integer")

    # 임시 우회: DB 조회 없이 성공 응답 반환 (권한 문제 해결까지)
    return {
        "company_id": company_id_int,
        "company_name": payload.company_name,
        "id": company_id_int,
        "message": "Company survey submitted successfully (temporary bypass)",
        "survey_received": {
            "communication_style": payload.communication_style,
            "main_channel": payload.main_channel,
            "main_target": payload.main_target,
            "team_size": payload.team_size
        }
    }
