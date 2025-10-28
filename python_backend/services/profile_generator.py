from api.v1.schemas.survey import CompanySurvey
from services.openai_services import OpenAIService # Added import
import logging

logger = logging.getLogger('chattoner.profile_generator') # Added logger

class ProfileGeneratorService:
    def __init__(self, openai_service: OpenAIService): # Modified to inject OpenAIService
        self.openai_service = openai_service

    async def create_profile_from_survey(self, survey_data: CompanySurvey) -> str: # Made async
        """Generate communication profile text by calling LLM based on survey data"""

        channels = ", ".join(survey_data.main_channel)
        targets = ", ".join(survey_data.main_target)

        prompt = f"""
        다음은 '{survey_data.company_name}' 회사의 커뮤니케이션 설문 요약입니다.
        - 산업 분야: {survey_data.industry}
        - 주요 사업: {survey_data.primary_business}
        - 팀 인원: {survey_data.team_size}명
        - 주 소통 성격: {survey_data.communication_style}
        - 주 소통 채널: {channels}
        - 주요 대상: {targets}

        위 특성을 고려하여, 신입사원이 바로 적용할 수 있는 회사 맞춤 커뮤니케이션 프로필을 작성하세요.
        - 항목 수: 2~4개 핵심 원칙
        - 형식: 번호 목록, 각 항목 1문장
        - 톤: 명확·실무적, 불필요한 수사는 지양
        - 준수사항: 기업 맥락/대상/채널에 맞는 예시 용어와 포맷 언급 가능
        """
        
        logger.info(f"--- LLM에 전달할 프롬프트 ---\n{prompt}") # Changed print to logger
        
        # Actual OpenAI API call
        try:
            profile_text = await self.openai_service.generate_text(prompt) # Actual LLM call
            logger.info("기업 프로필 LLM 생성 완료")
            return profile_text.strip()
        except Exception as e:
            logger.error(f"기업 프로필 LLM 생성 실패: {e}")
            # Fallback to a generic profile if LLM call fails
            return (
                "1. 핵심 메시지를 먼저 전달하고, 필요 시 근거와 예시를 덧붙입니다.\n"
                "2. 합의된 채널과 포맷을 준수하며, 대상에 맞춘 격식과 어조를 유지합니다."
            ).strip()

    # vectorize_and_save was removed; vectorization handled elsewhere
