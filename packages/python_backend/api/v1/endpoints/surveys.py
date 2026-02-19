from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
import logging

from datetime import datetime # Added import
from services.openai_services import OpenAIService
from services.company_profile_service import CompanyProfileService

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
    companyProfile: str  # 회사 맞춤형 커뮤니케이션 가이드
    companyContext: Dict[str, Any]  # 회사 특성 정보
    surveyResponses: Dict[str, Any]  # 원본 설문 응답
    createdAt: str
    message: Optional[str] = None
    profileType: str = "company_based"

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "id": 1,
                    "userId": "u1",
                    "companyProfile": "## 스타트업/소규모 engineering 팀 커뮤니케이션 가이드\n\n### 핵심 원칙\n1. **기술적 정확성**: 구체적인 기술 용어와 명확한 문제 정의\n2. **빠른 피드백**: 이슈 발생 시 즉시 공유하여 신속한 해결\n3. **협업 중심**: 코드 리뷰와 페어 프로그래밍을 통한 지식 공유\n\n### 상황별 가이드\n- **데일리 미팅**: 진행 상황과 블로커를 간결하게 공유\n- **이메일/슬랙**: 기술적 이슈는 스크린샷과 로그 첨부\n- **코드 리뷰**: 건설적 피드백으로 개선점 제시",
                    "companyContext": {
                        "companySize": "스타트업/소규모",
                        "teamSize": "1-10",
                        "primaryFunction": "engineering",
                        "communicationStyle": "friendly",
                        "primaryChannel": "email"
                    },
                    "surveyResponses": {"primary_function": "engineering", "communication_style": "friendly"},
                    "createdAt": "2025-10-29T12:00:00Z",
                    "message": "팀 특성에 맞는 커뮤니케이션 가이드를 생성했습니다.",
                    "profileType": "company_based"
                }
            ]
        }


@router.post(
    "/{key}/responses",
    response_model=OnboardingSurveyResponse,
    status_code=200,
    responses={
        200: {
            "description": "유효한 설문 응답 시 200 OK를 반환하고 생성된 회사 프로필을 JSON 파일에 저장합니다.",
            "content": {"application/json": {"examples": OnboardingSurveyResponse.Config.json_schema_extra["examples"]}},
        }
    }
)
async def submit_survey(key: str, req: SubmitRequest):
    if key != "onboarding-intake":
        raise HTTPException(404, "unknown survey key")

    logger.info(f"=== 설문 제출 시작 ===")
    logger.info(f"User ID: {req.user_id}")
    logger.info(f"Survey answers: {req.answers}")

    try:
        # 회사 프로필 생성 서비스 사용
        logger.info("CompanyProfileService 인스턴스 생성 중...")
        company_profile_service = CompanyProfileService()
        logger.info("CompanyProfileService 생성 완료, generate_company_profile 호출 중...")

        profile_data = await company_profile_service.generate_company_profile(
            user_id=req.user_id,
            survey_answers=req.answers
        )
        logger.info(f"CompanyProfileService.generate_company_profile 성공완료!")
        logger.info(f"생성된 프로필 데이터: {profile_data}")

        # 온보딩 완료 메시지 생성
        try:
            oai = OpenAIService()
            ob_msg = await oai.generate_text(
                (
                    f"팀 특성({profile_data['companyContext']['companySize']}, {profile_data['companyContext']['primaryFunction']})에 맞는 "
                    "커뮤니케이션 가이드를 생성했습니다. 실무에서 바로 활용해보세요!"
                ),
                temperature=0.3,
                max_tokens=100,
            )
        except Exception:
            ob_msg = "팀 특성에 맞는 커뮤니케이션 가이드를 생성했습니다."

        return OnboardingSurveyResponse(
            id=profile_data["id"],
            userId=profile_data["userId"],
            companyProfile=profile_data["generatedProfile"],
            companyContext=profile_data["companyContext"],
            surveyResponses=profile_data["surveyResponses"],
            createdAt=profile_data["createdAt"],
            message=ob_msg,
            profileType=profile_data["profileType"]
        )

    except Exception as e:
        # 폴백: 실패 시에도 기본 프로필 반환
        logger.error(f"=== 회사 프로필 생성 실패 ===")
        logger.error(f"오류: {e}")
        logger.error(f"오류 타입: {type(e)}")
        logger.error("전체 스택 트레이스:", exc_info=True)
        logger.error("기본 프로필로 폴백 처리합니다.")

        fallback_context = {
            "companySize": "일반 조직",
            "teamSize": req.answers.get("team_size", "알 수 없음"),
            "primaryFunction": req.answers.get("primary_function", "일반"),
            "communicationStyle": req.answers.get("communication_style", "친근함"),
            "primaryChannel": req.answers.get("primary_channel", "이메일")
        }

        fallback_profile = f"""
## {fallback_context['companySize']} 커뮤니케이션 가이드

### 핵심 원칙
1. **명확성**: 목적과 기대사항을 구체적으로 전달
2. **효율성**: 체계적이고 간결한 소통
3. **협업**: 팀워크를 고려한 건설적인 대화

### 기본 가이드
- **회의**: 안건 중심의 효율적인 진행
- **메시지**: 요점을 앞세운 명확한 전달
- **보고**: 결과와 다음 단계를 명시

실무에서 상황에 맞게 조정하여 사용하세요.
"""

        return OnboardingSurveyResponse(
            id=1,
            userId=req.user_id,
            companyProfile=fallback_profile,
            companyContext=fallback_context,
            surveyResponses=req.answers,
            createdAt=datetime.now().isoformat(),
            message="기본 커뮤니케이션 가이드를 생성했습니다.",
            profileType="company_based"
        )


# Company survey endpoints temporarily disabled - require PostgreSQL EnterpriseDBService
# TODO: Implement SQLite-based company survey storage when needed
