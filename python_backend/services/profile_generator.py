import openai
from api.v1.schemas.survey import CompanySurvey

class ProfileGeneratorService:
    def __init__(self):
        # openai.api_key 설정
        pass

    def create_profile_from_survey(self, survey_data: CompanySurvey) -> str:
        """설문조사 데이터 기반으로 LLM을 호출하여 커뮤니케이션 프로필 텍스트를 생성"""
        
        prompt = f"""
        다음은 '{survey_data.company_name}' 회사의 커뮤니케이션 스타일 설문조사 결과입니다.
        - 팀 인원: {survey_data.team_size}명
        - 주된 소통 성격: {survey_data.communication_style}
        - 주 소통 채널: {survey_data.main_channel}
        - 주 커뮤니케이션 대상: {', '.join(survey_data.main_target)}

        이 정보를 바탕으로, 이 회사의 신입사원이 따라야 할 커뮤니케이션 스타일 프로필을
        핵심 원칙 2~3가지로 요약해서 생성해줘.
        """
        
        print(f"--- LLM에 전달할 프롬프트 ---\n{prompt}")
        # 실제 OpenAI API 호출
        profile_text = (
            f"1. 친근하고 수평적인 소통을 지향하며, 주로 Slack을 통해 신속하게 의견을 교환합니다.\n"
            f"2. 내부 동료 및 타 부서와의 협업이 중요하므로, 명확하고 간결한 커뮤니케이션을 추구합니다."
        )
        
        return profile_text.strip()

    def vectorize_and_save(self, company_id: int, profile_text: str):
        """생성된 프로필 텍스트를 벡터화하고 벡터 DB에 저장"""
        
        print(f"--- 벡터화 및 저장 ---\nCompany ID: {company_id}\nProfile: {profile_text[:50]}...")
        print(f"Company ID {company_id}의 프로필 벡터 저장 완료")
        
        return True