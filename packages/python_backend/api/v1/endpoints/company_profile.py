"""
회사 프로필 생성 엔드포인트
설문 응답을 기반으로 회사 특성에 맞는 커뮤니케이션 가이드 생성
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging

from services.company_profile_service import CompanyProfileService

logger = logging.getLogger('chattoner.company_profile')

router = APIRouter()


class CompanyProfileRequest(BaseModel):
    tenant_id: str
    user_id: str
    answers: Dict[str, Any]

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "company-1",
                "user_id": "user-123",
                "answers": {
                    "primary_function": "engineering",
                    "communication_style": "friendly",
                    "team_size": "1-10",
                    "primary_channel": "email",
                    "primary_audience": ["peers_internal", "cross_team"]
                }
            }
        }


class CompanyProfileResponse(BaseModel):
    id: int
    userId: str
    companyProfile: str  # 회사 맞춤형 커뮤니케이션 가이드
    companyContext: Dict[str, Any]  # 회사 특성 정보
    surveyResponses: Dict[str, Any]  # 원본 설문 응답
    createdAt: str
    message: Optional[str] = None
    profileType: str = "company_based"


@router.post(
    "/generate",
    response_model=CompanyProfileResponse,
    status_code=200,
    summary="회사 맞춤 프로필 생성",
    description="설문 응답을 기반으로 회사 특성에 맞는 커뮤니케이션 가이드를 생성합니다."
)
async def generate_company_profile(req: CompanyProfileRequest):
    """
    ## 회사 맞춤 프로필 생성

    설문 응답을 분석하여 회사 규모, 업무 특성, 소통 스타일 등을 고려한
    실용적인 커뮤니케이션 가이드를 생성합니다.

    ### 생성되는 가이드 내용:
    - 팀 규모와 업무 특성에 맞는 커뮤니케이션 원칙
    - 상황별(회의, 이메일, 보고서) 톤앤매너 가이드
    - 업무 분야별 효과적인 표현법
    """

    try:
        # 회사 프로필 생성 서비스 사용
        company_profile_service = CompanyProfileService()
        profile_data = await company_profile_service.generate_company_profile(
            user_id=req.user_id,
            survey_answers=req.answers
        )

        return CompanyProfileResponse(
            id=profile_data["id"],
            userId=profile_data["userId"],
            companyProfile=profile_data["generatedProfile"],
            companyContext=profile_data["companyContext"],
            surveyResponses=profile_data["surveyResponses"],
            createdAt=profile_data["createdAt"],
            message=f"'{profile_data['companyContext']['companySize']}' 규모의 '{profile_data['companyContext']['primaryFunction']}' 팀에 맞는 커뮤니케이션 가이드를 생성했습니다.",
            profileType=profile_data["profileType"]
        )

    except Exception as e:
        logger.error(f"회사 프로필 생성 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"회사 프로필 생성 중 오류가 발생했습니다: {str(e)}")


@router.get(
    "/{user_id}",
    response_model=CompanyProfileResponse,
    summary="회사 프로필 조회",
    description="저장된 회사 프로필을 조회합니다."
)
async def get_company_profile(user_id: str):
    """
    ## 회사 프로필 조회

    사용자 ID로 저장된 회사 프로필을 조회합니다.
    """

    try:
        company_profile_service = CompanyProfileService()
        profile_data = company_profile_service.get_profile(user_id)

        if not profile_data:
            raise HTTPException(status_code=404, detail=f"사용자 '{user_id}'의 프로필을 찾을 수 없습니다.")

        return CompanyProfileResponse(
            id=profile_data["id"],
            userId=profile_data["userId"],
            companyProfile=profile_data["generatedProfile"],
            companyContext=profile_data["companyContext"],
            surveyResponses=profile_data["surveyResponses"],
            createdAt=profile_data["createdAt"],
            message=None,
            profileType=profile_data["profileType"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"프로필 조회 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"프로필 조회 중 오류가 발생했습니다: {str(e)}")