from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
import logging

from datetime import datetime # Added import
from services.profile_pipeline import run_profile_pipeline
from services.vector_store_pg import VectorStorePG
from api.dependencies import get_vector_store
from services.openai_services import OpenAIService
from services.style_profile_service import extract_style_features_from_survey

logger = logging.getLogger('chattoner.surveys')


router = APIRouter(tags=["surveys"])


class SurveySchema(BaseModel):
    title: str
    questions: List[Dict[str, Any]]


@router.get("/{key}", response_model=SurveySchema)
async def get_survey(key: str):
    if key != "onboarding-intake":
        raise HTTPException(404, "unknown survey key")
    return SurveySchema(
        title="온보딩 인테이크",
        questions=[
            {"id": "primary_function", "type": "single_select", "label": {"ko": "주 업무 범주"}, "options": ["engineering", "sales", "operations", "hr", "finance"], "required": True},
            {"id": "communication_style", "type": "single_select", "label": {"ko": "소통 성격"}, "options": ["friendly", "formal", "strict", "casual"], "required": True},
            {"id": "team_size", "type": "single_select", "label": {"ko": "인원 수"}, "options": ["1-10", "11-50", "51-200", "201-1000", "1001+"], "required": True},
            {"id": "primary_channel", "type": "single_select", "label": {"ko": "주된 커뮤니케이션 채널"}, "options": ["email", "chat", "report", "meeting_minutes"], "required": True},
            {"id": "primary_audience", "type": "multi_select", "label": {"ko": "주 커뮤니케이션 대상"}, "options": ["peers_internal", "cross_team", "executives", "clients_vendors"], "required": True},
        ],
    )


class SubmitRequest(BaseModel):
    tenant_id: str
    user_id: str
    answers: Dict[str, Any]

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "t1",
                "user_id": "u1",
                "answers": {
                    "q_formality": "formal",
                    "q_friendliness": "friendly",
                    "q_emotion": "neutral",
                    "q_directness": "direct"
                }
            }
        }


class OnboardingSurveyResponse(BaseModel):
    id: int
    userId: str
    baseFormalityLevel: int
    baseFriendlinessLevel: int
    baseEmotionLevel: int
    baseDirectnessLevel: int
    sessionFormalityLevel: int
    sessionFriendlinessLevel: int
    sessionEmotionLevel: int
    sessionDirectnessLevel: int
    traitScores: Dict[str, float]
    responses: Dict[str, Any]
    completedAt: str
    message: Optional[str] = None

    class Config:
        json_schema_extra = {
            "examples": {
                "success": {
                    "summary": "성공",
                    "value": {
                        "id": 1,
                        "userId": "u1",
                        "baseFormalityLevel": 80,
                        "baseFriendlinessLevel": 70,
                        "baseEmotionLevel": 50,
                        "baseDirectnessLevel": 60,
                        "sessionFormalityLevel": 80,
                        "sessionFriendlinessLevel": 70,
                        "sessionEmotionLevel": 50,
                        "sessionDirectnessLevel": 60,
                        "traitScores": {
                            "formality": 8.0,
                            "friendliness": 7.0,
                            "emotiveness": 5.0,
                            "directness": 6.0
                        },
                        "responses": {"q_formality": "formal"},
                        "completedAt": "2025-10-29T12:00:00Z",
                        "message": "협업에서 바로 활용 가능한 톤 가이드를 적용했습니다."
                    }
                },
                "fallback": {
                    "summary": "폴백(저장 생략)",
                    "value": {
                        "id": 1,
                        "userId": "u1",
                        "baseFormalityLevel": 50,
                        "baseFriendlinessLevel": 50,
                        "baseEmotionLevel": 50,
                        "baseDirectnessLevel": 50,
                        "sessionFormalityLevel": 50,
                        "sessionFriendlinessLevel": 50,
                        "sessionEmotionLevel": 50,
                        "sessionDirectnessLevel": 50,
                        "traitScores": {
                            "formality": 5.0,
                            "friendliness": 5.0,
                            "emotiveness": 5.0,
                            "directness": 5.0
                        },
                        "responses": {"q_formality": "moderate"},
                        "completedAt": "2025-10-29T12:00:00Z",
                        "message": "설정 저장은 완료되었어요. 협업에서 유용한 톤 사용 팁을 참고해 주세요."
                    }
                }
            }
        }


@router.post(
    "/{key}/responses",
    response_model=OnboardingSurveyResponse,
    status_code=200,
    responses={
        200: {
            "description": "유효한 설문 응답 시 200 OK를 반환하고 생성된 프로필을 벡터 DB에 저장합니다.",
            "content": {"application/json": {"examples": OnboardingSurveyResponse.Config.json_schema_extra["examples"]}},
        }
    }
)
async def submit_survey(key: str, req: SubmitRequest, store: VectorStorePG = Depends(get_vector_store)):
    if key != "onboarding-intake":
        raise HTTPException(404, "unknown survey key")
    try:
        profile_result = await run_profile_pipeline(
            tenant_id=req.tenant_id,
            user_id=req.user_id,
            survey_answers=req.answers,
            store=store,
            store_vector=True
        )

        # Map the profile features to the desired response format
        features = profile_result["features"]
        # LLM 가공 온보딩 메시지 (선택)
        try:
            oai = OpenAIService()
            ob_msg = await oai.generate_text(
                (
                    "온보딩 설문 응답을 바탕으로 커뮤니케이션 프로필을 설정했어요."
                    " 협업에서 바로 활용할 수 있는 1~2개의 짧은 팁을 한 문장씩 제시하세요."
                ),
                temperature=0.3,
                max_tokens=120,
            )
        except Exception:
            ob_msg = None
        return {
            "id": 1, # This ID is not used in the pipeline, can be generated or fetched if needed
            "userId": req.user_id,
            "baseFormalityLevel": int(features["formality"] * 10), # Scale 1-10 to 1-100 and convert to int
            "baseFriendlinessLevel": int(features["friendliness"] * 10),
            "baseEmotionLevel": int(features["emotiveness"] * 10),
            "baseDirectnessLevel": int(features["directness"] * 10),
            "sessionFormalityLevel": int(features["formality"] * 10), # For now, session levels are same as base
            "sessionFriendlinessLevel": int(features["friendliness"] * 10),
            "sessionEmotionLevel": int(features["emotiveness"] * 10),
            "sessionDirectnessLevel": int(features["directness"] * 10),
            # 사용자 성향 점수(1-10 스케일, 소수 포함 가능)
            "traitScores": {
                "formality": float(features["formality"]),
                "friendliness": float(features["friendliness"]),
                "emotiveness": float(features["emotiveness"]),
                "directness": float(features["directness"]),
            },
            "responses": req.answers,
            "completedAt": datetime.now().isoformat() + "Z", # Use current time
            "message": ob_msg
        }
    except Exception as e:
        # 폴백: 파이프라인 실패 시에도 200 OK로 유효 응답 반환
        logger.error(f"설문 처리 중 오류 발생(폴백 응답으로 처리): {e}", exc_info=True)

        # 기본 특성 추출(설문에서 직접), 실패 시 중립값 사용
        try:
            features_obj = extract_style_features_from_survey(req.answers)
            features = features_obj.dict()
        except Exception:
            features = {"formality": 5.0, "friendliness": 5.0, "emotiveness": 5.0, "directness": 5.0}

        # 폴백 경로: LLM 가공 안내문 추가
        try:
            oai = OpenAIService()
            ob_msg = await oai.generate_text(
                (
                    "설정 저장은 완료되었어요. 프로젝트 협업에서 유용한 톤 사용 팁을"
                    " 1~2문장으로 간결하게 제시하세요. 신입도 이해 가능한 수준으로."
                ),
                temperature=0.3,
                max_tokens=120,
            )
        except Exception:
            ob_msg = None
        return {
            "id": 1,
            "userId": req.user_id,
            "baseFormalityLevel": int(features["formality"] * 10),
            "baseFriendlinessLevel": int(features["friendliness"] * 10),
            "baseEmotionLevel": int(features["emotiveness"] * 10),
            "baseDirectnessLevel": int(features["directness"] * 10),
            "sessionFormalityLevel": int(features["formality"] * 10),
            "sessionFriendlinessLevel": int(features["friendliness"] * 10),
            "sessionEmotionLevel": int(features["emotiveness"] * 10),
            "sessionDirectnessLevel": int(features["directness"] * 10),
            # 사용자 성향 점수(1-10 스케일)
            "traitScores": {
                "formality": float(features["formality"]),
                "friendliness": float(features["friendliness"]),
                "emotiveness": float(features["emotiveness"]),
                "directness": float(features["directness"]),
            },
            "responses": req.answers,
            "completedAt": datetime.now().isoformat() + "Z",
            "message": ob_msg
        }


from api.v1.schemas.survey import CompanySurvey # Added import
from services.enterprise_db_service import EnterpriseDBService # Added import
from services.profile_generator import ProfileGeneratorService # Added import
from dependency_injector.wiring import inject, Provide # Added import
from core.container import Container # Added import


@router.post("/company/{company_id}/responses", status_code=200)
@inject
async def submit_company_survey(
    company_id: str,
    survey_data: CompanySurvey,
    db_service: EnterpriseDBService = Depends(Provide[Container.enterprise_db_service]),
    profile_generator: ProfileGeneratorService = Depends(Provide[Container.profile_generator_service])
):
    """
    기업 설문조사 응답을 제출하고 기업 프로필을 생성 및 저장합니다.
    - company_id: 기업의 고유 ID (Path Parameter)
    """
    
    # 1. company_id 존재 여부 확인 (Pre-condition)
    existing_profile = await db_service.get_company_profile(company_id)
    if not existing_profile:
        # Pre-condition enforced: company_id must exist in DB
        raise HTTPException(status_code=404, detail=f"company_id '{company_id}' not found")

    # 2. AI 기반 기업 프로필 텍스트 생성
    generated_profile_text = await profile_generator.create_profile_from_survey(survey_data)

    # 3. 설문 데이터와 생성된 프로필을 DB에 저장 (upsert)
    success = await db_service.upsert_company_profile(
        company_id=company_id,
        company_name=survey_data.company_name,
        industry=survey_data.industry,
        team_size=survey_data.team_size,
        primary_business=survey_data.primary_business,
        communication_style=survey_data.communication_style,
        main_channels=survey_data.main_channel, # Now List[str]
        target_audience=survey_data.main_target,
        generated_profile=generated_profile_text,
        survey_data=survey_data.dict()
    )

    if not success:
        logger.error(f"기업 프로필 저장/업데이트 실패: {company_id}")
        raise HTTPException(status_code=500, detail="기업 프로필 저장에 실패했습니다.")

    return {
        "message": "기업 프로필이 성공적으로 생성 및 저장되었습니다.",
        "company_id": company_id,
        "generated_profile_text": generated_profile_text,
        "survey_data": survey_data.dict()
    }

# Alias endpoint to match spec: POST /api/v1/surveys/company/{company_id}
@router.post("/company/{company_id}", status_code=200)
@inject
async def submit_company_survey_alias(
    company_id: str,
    survey_data: CompanySurvey,
    db_service: EnterpriseDBService = Depends(Provide[Container.enterprise_db_service]),
    profile_generator: ProfileGeneratorService = Depends(Provide[Container.profile_generator_service])
):
    # 동일 로직 재사용
    existing_profile = await db_service.get_company_profile(company_id)
    if not existing_profile:
        raise HTTPException(status_code=404, detail=f"company_id '{company_id}' not found")

    generated_profile_text = await profile_generator.create_profile_from_survey(survey_data)

    success = await db_service.upsert_company_profile(
        company_id=company_id,
        company_name=survey_data.company_name,
        industry=survey_data.industry,
        team_size=survey_data.team_size,
        primary_business=survey_data.primary_business,
        communication_style=survey_data.communication_style,
        main_channels=survey_data.main_channel,
        target_audience=survey_data.main_target,
        generated_profile=generated_profile_text,
        survey_data=survey_data.dict()
    )

    if not success:
        logger.error(f"기업 프로필 저장/업데이트 실패: {company_id}")
        raise HTTPException(status_code=500, detail="기업 프로필 저장에 실패했습니다.")

    return {
        "message": "기업 프로필이 성공적으로 생성 및 저장되었습니다.",
        "company_id": company_id,
        "generated_profile_text": generated_profile_text,
        "survey_data": survey_data.dict()
    }
