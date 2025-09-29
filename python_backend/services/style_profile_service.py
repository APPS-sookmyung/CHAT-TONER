"""
사용자 스타일 프로필 생성 서비스
설문조사 답변을 기반으로 개인화된 톤 변환 프로필을 생성
"""

from typing import Any, Dict, Optional
from dataclasses import dataclass


@dataclass
class StyleFeatures:
    """스타일 특성 데이터 클래스"""
    formality: float = 5.0  # 격식도 (1-10)
    friendliness: float = 5.0  # 친근함 (1-10)
    emotiveness: float = 5.0  # 감정표현 (1-10)
    directness: float = 5.0  # 직설성 (1-10)

    def dict(self) -> Dict[str, float]:
        """딕셔너리로 변환"""
        return {
            'formality': self.formality,
            'friendliness': self.friendliness,
            'emotiveness': self.emotiveness,
            'directness': self.directness
        }


@dataclass
class StyleProfile:
    """스타일 프로필 데이터 클래스"""
    user_id: str
    tenant_id: str
    features: StyleFeatures
    prompt: str

    def dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'user_id': self.user_id,
            'tenant_id': self.tenant_id,
            'features': self.features.dict(),
            'prompt': self.prompt
        }


def build_style_profile(
    *,
    user_id: str,
    tenant_id: str,
    traits: Dict[str, Any],
    use_llm: bool = False
) -> StyleProfile:
    """
    사용자 특성을 기반으로 스타일 프로필 생성

    Args:
        user_id: 사용자 ID
        tenant_id: 테넌트 ID
        traits: 사용자 특성 (설문조사 답변 등)
        use_llm: LLM 사용 여부 (현재는 미구현)

    Returns:
        StyleProfile: 생성된 스타일 프로필
    """

    # 기본값 설정
    formality = float(traits.get('formality', 5))
    friendliness = float(traits.get('friendliness', 5))
    emotiveness = float(traits.get('emotiveness', 5))
    directness = float(traits.get('directness', 5))

    # 범위 검증 (1-10)
    formality = max(1.0, min(10.0, formality))
    friendliness = max(1.0, min(10.0, friendliness))
    emotiveness = max(1.0, min(10.0, emotiveness))
    directness = max(1.0, min(10.0, directness))

    features = StyleFeatures(
        formality=formality,
        friendliness=friendliness,
        emotiveness=emotiveness,
        directness=directness
    )

    # 프로필 텍스트 생성
    prompt = _generate_profile_prompt(features, traits)

    return StyleProfile(
        user_id=user_id,
        tenant_id=tenant_id,
        features=features,
        prompt=prompt
    )


def _generate_profile_prompt(features: StyleFeatures, traits: Dict[str, Any]) -> str:
    """특성 기반 프로필 프롬프트 생성"""

    # 격식도 분석
    if features.formality >= 8:
        formality_desc = "매우 격식있고 공손한 언어를 사용"
    elif features.formality >= 6:
        formality_desc = "적당히 격식있는 언어를 사용"
    elif features.formality >= 4:
        formality_desc = "자연스럽고 편안한 언어를 사용"
    else:
        formality_desc = "캐주얼하고 친숙한 언어를 사용"

    # 친근함 분석
    if features.friendliness >= 8:
        friendliness_desc = "따뜻하고 친밀한 톤으로 소통"
    elif features.friendliness >= 6:
        friendliness_desc = "친근하고 상냥한 톤으로 소통"
    elif features.friendliness >= 4:
        friendliness_desc = "중립적이고 예의바른 톤으로 소통"
    else:
        friendliness_desc = "간결하고 사무적인 톤으로 소통"

    # 감정표현 분석
    if features.emotiveness >= 8:
        emotiveness_desc = "감정과 열정을 풍부하게 표현"
    elif features.emotiveness >= 6:
        emotiveness_desc = "적절한 감정 표현을 포함"
    elif features.emotiveness >= 4:
        emotiveness_desc = "절제된 감정 표현을 사용"
    else:
        emotiveness_desc = "감정 표현을 최소화하고 객관적으로 서술"

    # 직설성 분석
    if features.directness >= 8:
        directness_desc = "명확하고 직접적인 표현을 선호"
    elif features.directness >= 6:
        directness_desc = "분명하면서도 배려있는 표현을 사용"
    elif features.directness >= 4:
        directness_desc = "완곡하고 신중한 표현을 사용"
    else:
        directness_desc = "매우 완곡하고 조심스러운 표현을 사용"

    # 추가 특성 반영
    primary_channel = traits.get('primary_channel', 'email')
    communication_style = traits.get('communication_style', 'balanced')

    prompt = f"""사용자 커뮤니케이션 프로필:

핵심 특성:
- {formality_desc}하며, {friendliness_desc}합니다
- {emotiveness_desc}하고, {directness_desc}합니다
- 주요 소통 채널: {primary_channel}
- 전반적인 소통 스타일: {communication_style}

수치적 특성:
- 격식도: {features.formality}/10
- 친근함: {features.friendliness}/10
- 감정표현: {features.emotiveness}/10
- 직설성: {features.directness}/10

이 프로필에 맞춰 텍스트를 변환할 때는 위 특성을 종합적으로 고려하여
사용자의 개성과 선호도가 잘 반영되도록 조정해주세요."""

    return prompt


def extract_style_features_from_survey(survey_data: Dict[str, Any]) -> StyleFeatures:
    """설문조사 데이터에서 스타일 특성 추출"""

    # 설문 응답을 특성으로 매핑
    formality = _map_survey_to_scale(survey_data.get('q_formality'), 'formality')
    friendliness = _map_survey_to_scale(survey_data.get('q_friendliness'), 'friendliness')
    emotiveness = _map_survey_to_scale(survey_data.get('q_emotion'), 'emotiveness')
    directness = _map_survey_to_scale(survey_data.get('q_directness'), 'directness')

    return StyleFeatures(
        formality=formality,
        friendliness=friendliness,
        emotiveness=emotiveness,
        directness=directness
    )


def _map_survey_to_scale(survey_value: Any, feature_type: str) -> float:
    """설문 응답을 1-10 스케일로 변환"""

    if survey_value is None:
        return 5.0  # 기본값

    # 숫자형 응답 처리
    if isinstance(survey_value, (int, float)):
        return max(1.0, min(10.0, float(survey_value)))

    # 문자형 응답 처리
    if isinstance(survey_value, str):
        survey_value = survey_value.lower()

        # 일반적인 매핑
        mapping = {
            'very_low': 2.0, 'low': 3.5, 'moderate': 5.0,
            'high': 7.0, 'very_high': 8.5,
            'formal': 8.0, 'casual': 3.0, 'balanced': 5.0,
            'direct': 8.0, 'indirect': 3.0, 'moderate': 5.0,
            'expressive': 8.0, 'reserved': 3.0, 'neutral': 5.0,
            'friendly': 8.0, 'professional': 6.0, 'distant': 3.0
        }

        return mapping.get(survey_value, 5.0)

    return 5.0  # 기본값


# 사용 예시
if __name__ == "__main__":
    # 테스트 데이터
    test_traits = {
        'formality': 7,
        'friendliness': 6,
        'emotiveness': 4,
        'directness': 8,
        'primary_channel': 'email',
        'communication_style': 'professional'
    }

    profile = build_style_profile(
        user_id="test_user",
        tenant_id="test_tenant",
        traits=test_traits,
        use_llm=False
    )

    print("Generated Profile:")
    print(f"User ID: {profile.user_id}")
    print(f"Features: {profile.features.dict()}")
    print(f"Prompt:\n{profile.prompt}")