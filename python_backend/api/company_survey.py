from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.v1.schemas.survey import CompanySurvey
from services.profile_generator import ProfileGeneratorService
from database.db import get_db
from database.models import CompanyProfile

router = APIRouter(
    prefix="/surveys",
    tags=["Company Survey"]
)

@router.post("/company/{company_id}")
def submit_company_survey(
    company_id: int,
    survey_data: CompanySurvey,
    profile_service: ProfileGeneratorService = Depends(),
    db: Session = Depends(get_db)
):
    """
    기업용 설문조사를 제출받아 처리하는 엔드포인트입니다.
    1. 설문 응답을 기반으로 커뮤니케이션 프로필을 생성합니다.
    2. 생성된 프로필을 벡터화하여 Vector DB에 저장합니다.
    3. 설문 원본 데이터와 생성된 프로필을 RDB에 저장합니다.
    """
    # 프로필 생성 및 벡터화 로직
    profile_text = profile_service.create_profile_from_survey(survey_data)
    if "실패" in profile_text:
        raise HTTPException(status_code=500, detail="커뮤니케이션 프로필 생성에 실패했습니다.")
    profile_service.vectorize_and_save(company_id, profile_text)
    
    # DB에서 해당 company_id를 가진 회사 프로필 탐색 또는 생성
    company_profile = db.query(CompanyProfile).filter(CompanyProfile.id == company_id).first()

    if not company_profile:
        # 회사 프로필이 없으면 새로 생성
        company_profile = CompanyProfile(
            id=company_id,
            company_name=survey_data.company_name,  # 설문조사에서 회사명 가져오기
            survey_data=survey_data.model_dump(),
            generated_profile=profile_text
        )
        db.add(company_profile)
    else:
        # 기존 회사 프로필 업데이트
        company_profile.company_name = survey_data.company_name
        company_profile.survey_data = survey_data.model_dump()
        company_profile.generated_profile = profile_text
    
    # 변경 내용을 데이터베이스에 최종 저장
    db.commit()
    # DB에 저장된 최신 정보로 현재 객체 업데이트
    db.refresh(company_profile)

    return {
        "message": "설문조사가 성공적으로 처리 및 저장되었습니다.",
        "company_id": company_id,
        "saved_data": {
            "survey": company_profile.survey_data,
            "profile": company_profile.generated_profile
        }
    }