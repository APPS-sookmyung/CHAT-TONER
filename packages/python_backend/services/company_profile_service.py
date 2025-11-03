"""
회사 프로필 생성 및 JSON 저장 서비스
설문 응답을 기반으로 회사 특성에 맞는 커뮤니케이션 가이드를 생성합니다.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from services.openai_services import OpenAIService


class CompanyProfileService:
    def __init__(self):
        self.data_dir = "database"
        self.profiles_file = os.path.join(self.data_dir, "company_profiles.json")
        self._ensure_data_dir()

    def _ensure_data_dir(self):
        """데이터 디렉토리가 없으면 생성"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

        if not os.path.exists(self.profiles_file):
            with open(self.profiles_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)

    def _load_profiles(self) -> Dict[str, Any]:
        """JSON 파일에서 프로필 데이터 로드"""
        try:
            with open(self.profiles_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_profiles(self, profiles: Dict[str, Any]):
        """프로필 데이터를 JSON 파일에 저장"""
        with open(self.profiles_file, 'w', encoding='utf-8') as f:
            json.dump(profiles, f, ensure_ascii=False, indent=2)

    async def generate_company_profile(self, user_id: str, survey_answers: Dict[str, Any]) -> Dict[str, Any]:
        """
        설문 응답을 기반으로 회사 맞춤형 커뮤니케이션 프로필 생성
        """
        print(f"[CompanyProfile] generate_company_profile 시작")
        print(f"[CompanyProfile] user_id: {user_id}")
        print(f"[CompanyProfile] survey_answers: {survey_answers}")

        # 설문 응답 해석
        team_size = survey_answers.get("team_size", "1-10")
        primary_function = survey_answers.get("primary_function", "engineering")
        communication_style = survey_answers.get("communication_style", "friendly")
        primary_channel = survey_answers.get("primary_channel", "email")
        primary_audience = survey_answers.get("primary_audience", [])

        print(f"[CompanyProfile] 추출된 값들: team_size={team_size}, function={primary_function}, style={communication_style}")

        # 회사 특성 분석
        print("[CompanyProfile] 회사 컨텍스트 분석 시작...")
        company_context = self._analyze_company_context(survey_answers)
        print(f"[CompanyProfile] 회사 컨텍스트 분석 완료: {company_context}")

        # OpenAI를 사용하여 맞춤형 커뮤니케이션 가이드 생성
        print("[CompanyProfile] OpenAI 서비스 초기화 및 프로필 생성 시작...")
        try:
            oai = OpenAIService()
            print("[CompanyProfile] OpenAI 서비스 생성 완료")
            profile_prompt = f"""
다음 회사 정보를 바탕으로 실용적인 커뮤니케이션 가이드를 작성해주세요:

**회사 정보:**
- 팀 규모: {team_size}
- 주요 업무: {primary_function}
- 소통 스타일: {communication_style}
- 주요 채널: {primary_channel}
- 주요 대상: {', '.join(primary_audience) if primary_audience else '내부 팀원'}

**요청사항:**
1. 이 회사에 맞는 구체적인 커뮤니케이션 원칙 3가지
2. 각 상황별(회의, 이메일, 보고서) 톤앤매너 가이드
3. 해당 업무 분야에서 자주 쓰이는 효과적인 표현법

실무에서 바로 적용할 수 있도록 구체적이고 실용적으로 작성해주세요.
"""

            print(f"[CompanyProfile] 프롬프트 길이: {len(profile_prompt)} 문자")
            generated_profile = await oai.generate_text(
                profile_prompt,
                temperature=0.7,
                max_tokens=800
            )
            print(f"[CompanyProfile] OpenAI 프로필 생성 성공! 길이: {len(generated_profile)} 문자")

        except Exception as e:
            print(f"[CompanyProfile] OpenAI 프로필 생성 실패: {e}")
            print(f"[CompanyProfile] 폴백 프로필로 처리합니다...")
            # 폴백: 기본 템플릿 사용
            generated_profile = self._generate_fallback_profile(company_context)
            print(f"[CompanyProfile] 폴백 프로필 생성 완료")

        # 프로필 데이터 구성
        print("[CompanyProfile] 프로필 데이터 구성 중...")
        profile_data = {
            "id": len(self._load_profiles()) + 1,
            "userId": user_id,
            "companyContext": company_context,
            "generatedProfile": generated_profile,
            "surveyResponses": survey_answers,
            "createdAt": datetime.now().isoformat(),
            "profileType": "company_based"
        }
        print(f"[CompanyProfile] 프로필 데이터 구성 완료: {profile_data.keys()}")

        # JSON 파일에 저장
        print("[CompanyProfile] JSON 파일에 저장 시작...")
        profiles = self._load_profiles()
        profiles[user_id] = profile_data
        self._save_profiles(profiles)
        print(f"[CompanyProfile] JSON 파일 저장 완료! 총 프로필 수: {len(profiles)}")

        print("[CompanyProfile] CompanyProfileService.generate_company_profile 완전 성공!")
        return profile_data

    def _analyze_company_context(self, survey_answers: Dict[str, Any]) -> Dict[str, Any]:
        """설문 응답을 분석하여 회사 컨텍스트 추출"""
        team_size = survey_answers.get("team_size", "1-10")
        primary_function = survey_answers.get("primary_function", "engineering")
        communication_style = survey_answers.get("communication_style", "friendly")
        primary_channel = survey_answers.get("primary_channel", "email")
        primary_audience = survey_answers.get("primary_audience", [])

        # 회사 규모별 특성
        if team_size in ["1-10"]:
            company_size = "스타트업/소규모"
            size_characteristics = ["빠른 의사결정", "유연한 소통", "다양한 역할 수행"]
        elif team_size in ["11-50"]:
            company_size = "중소기업"
            size_characteristics = ["체계적 소통", "부서간 협업", "성장 단계의 조직"]
        elif team_size in ["51-200"]:
            company_size = "중견기업"
            size_characteristics = ["조직화된 프로세스", "전문성 중시", "효율적 업무 분담"]
        else:
            company_size = "대기업"
            size_characteristics = ["체계적 보고 체계", "공식적 소통", "계층적 구조"]

        # 업무 분야별 특성
        function_characteristics = {
            "engineering": ["기술적 정확성", "논리적 설명", "문제 해결 중심"],
            "sales": ["고객 중심", "설득력 있는 표현", "관계 구축"],
            "operations": ["효율성 강조", "프로세스 중심", "실행력"],
            "hr": ["사람 중심", "공감적 소통", "조직 문화"],
            "finance": ["정확성", "데이터 기반", "리스크 관리"]
        }.get(primary_function, ["전문성", "협업", "효율성"])

        return {
            "companySize": company_size,
            "teamSize": team_size,
            "primaryFunction": primary_function,
            "communicationStyle": communication_style,
            "primaryChannel": primary_channel,
            "primaryAudience": primary_audience,
            "sizeCharacteristics": size_characteristics,
            "functionCharacteristics": function_characteristics
        }

    def _generate_fallback_profile(self, company_context: Dict[str, Any]) -> str:
        """OpenAI 실패 시 사용할 기본 프로필 템플릿"""
        company_size = company_context["companySize"]
        primary_function = company_context["primaryFunction"]

        return f"""
## {company_size} {primary_function} 팀 커뮤니케이션 가이드

### 핵심 원칙
1. **명확성**: 목적과 기대사항을 구체적으로 전달
2. **효율성**: {company_context['primaryChannel']} 중심의 체계적 소통
3. **협업**: 팀 특성을 고려한 적절한 톤앤매너 유지

### 상황별 가이드
- **회의**: 안건 중심의 구조화된 대화
- **이메일**: 요점을 앞세운 간결한 작성
- **보고서**: 데이터와 결론을 명확히 구분

### 주요 표현법
{primary_function} 업무 특성에 맞는 전문적이면서도 협력적인 소통을 권장합니다.
"""

    def get_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """사용자 프로필 조회"""
        profiles = self._load_profiles()
        return profiles.get(user_id)

    def update_profile(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """프로필 업데이트"""
        profiles = self._load_profiles()
        if user_id in profiles:
            profiles[user_id].update(updates)
            profiles[user_id]["updatedAt"] = datetime.now().isoformat()
            self._save_profiles(profiles)
            return True
        return False