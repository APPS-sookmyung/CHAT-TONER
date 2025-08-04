
"""
사용자 선호도 관리 서비스 - 개선 버전
네거티브 프롬프트 선호도 및 스타일 학습 관리
"""

import logging
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional
from enum import Enum

from .base_service import BaseService
from database.storage import DatabaseStorage
from .openai_services import OpenAIService


class PreferenceLevel(Enum):
    """선호도 레벨 열거형"""
    STRICT = "strict"
    MODERATE = "moderate"
    LENIENT = "lenient"


class StyleType(Enum):
    """스타일 타입 열거형"""
    DIRECT = "direct"
    GENTLE = "gentle"
    NEUTRAL = "neutral"


@dataclass
class NegativePreferences:
    """네거티브 선호도 데이터 클래스"""
    user_id: str
    avoid_flowery_language: PreferenceLevel = PreferenceLevel.MODERATE
    avoid_repetitive_words: PreferenceLevel = PreferenceLevel.MODERATE
    comma_usage_style: PreferenceLevel = PreferenceLevel.MODERATE
    content_over_format: PreferenceLevel = PreferenceLevel.MODERATE
    bullet_point_usage: PreferenceLevel = PreferenceLevel.MODERATE
    emoticon_usage: PreferenceLevel = PreferenceLevel.MODERATE
    custom_negative_prompts: List[str] = None
    
    def __post_init__(self):
        if self.custom_negative_prompts is None:
            self.custom_negative_prompts = []
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        result = asdict(self)
        # Enum을 string으로 변환
        for key, value in result.items():
            if isinstance(value, PreferenceLevel):
                result[key] = value.value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NegativePreferences':
        """딕셔너리에서 생성"""
        # Enum 변환 처리- use field introspection for better maintainability
        from dataclasses import fields 
        for field in fields(cls):
            if field.type == PreferenceLevel and field.name in data and isinstance(data[field.name], str):
                data[field.name] = PreferenceLevel(data[field.name])
        return cls(**data)


@dataclass
class StyleAdjustment:
    """스타일 조정 데이터 클래스"""
    formality_delta: float = 0.0
    friendliness_delta: float = 0.0
    emotion_delta: float = 0.0
    directness_delta: float = 0.0
    
    def apply_factor(self, factor: float) -> 'StyleAdjustment':
        """팩터 적용하여 새로운 조정값 반환"""
        return StyleAdjustment(
            formality_delta=self._clamp_delta(self.formality_delta * factor),
            friendliness_delta=self._clamp_delta(self.friendliness_delta * factor),
            emotion_delta=self._clamp_delta(self.emotion_delta * factor),
            directness_delta=self._clamp_delta(self.directness_delta * factor)
        )
    
    @staticmethod
    def _clamp_delta(value: float, min_val: float = -0.5, max_val: float = 0.5) -> float:
        """델타값을 범위 내로 제한"""
        return max(min_val, min(max_val, value))


class PreferenceExtractor:
    """사용자 프로필에서 선호도 추출 전담 클래스"""
    
    @staticmethod
    def extract_from_profile(user_profile: Optional[Dict[str, Any]]) -> NegativePreferences:
        """사용자 프로필로부터 네거티브 선호도 추출"""
        if not user_profile:
            return PreferenceExtractor._get_default_preferences()
        
        user_id = user_profile.get('userId', 'unknown')
        formality = user_profile.get('baseFormalityLevel', 3)
        friendliness = user_profile.get('baseFriendlinessLevel', 3)
        emotion = user_profile.get('baseEmotionLevel', 3)
        directness = user_profile.get('baseDirectnessLevel', 3)
        
        return NegativePreferences(
            user_id=user_id,
            avoid_flowery_language=PreferenceExtractor._map_friendliness_to_flowery(friendliness, formality),
            avoid_repetitive_words=PreferenceExtractor._map_directness_to_repetitive(directness),
            comma_usage_style=PreferenceExtractor._map_friendliness_to_comma(friendliness),
            content_over_format=PreferenceExtractor._map_directness_to_content(directness),
            bullet_point_usage=PreferenceExtractor._map_formality_to_bullet(formality),
            emoticon_usage=PreferenceLevel.STRICT  # GPT스러워서 기본적으로 금지
        )
    
    @staticmethod
    def _get_default_preferences() -> NegativePreferences:
        """기본 선호도 반환"""
        return NegativePreferences(user_id='unknown')
    
    @staticmethod
    def _map_friendliness_to_flowery(friendliness: int, formality: int) -> PreferenceLevel:
        """친근함과 격식도 조합으로 미사여구 레벨 결정"""
        if friendliness >= 4 and formality <= 3:  # 친근하고 캐주얼할 때
            return PreferenceLevel.LENIENT
        elif formality <= 2:
            return PreferenceLevel.STRICT
        return PreferenceLevel.MODERATE
    
    @staticmethod
    def _map_directness_to_repetitive(directness: int) -> PreferenceLevel:
        """직설성에 따른 반복 회피 레벨 매핑"""
        return PreferenceLevel.STRICT if directness >= 4 else PreferenceLevel.MODERATE
    
    @staticmethod
    def _map_friendliness_to_comma(friendliness: int) -> PreferenceLevel:
        """친근함에 따른 쉼표 사용 레벨 매핑 - 친근할수록 자연스러운 쉼표 허용"""
        return PreferenceLevel.LENIENT if friendliness >= 4 else PreferenceLevel.MODERATE
    
    @staticmethod
    def _map_directness_to_content(directness: int) -> PreferenceLevel:
        """직설성에 따른 내용 우선도 레벨 매핑"""
        return PreferenceLevel.STRICT if directness >= 4 else PreferenceLevel.MODERATE
    
    @staticmethod
    def _map_formality_to_bullet(formality: int) -> PreferenceLevel:
        """격식도에 따른 불렛 포인트 사용 레벨 매핑"""
        return PreferenceLevel.STRICT if formality <= 2 else PreferenceLevel.MODERATE
    


class StyleLearningEngine:
    """스타일 학습 엔진 전담 클래스"""
    
    # 설정 상수들
    BASE_ADJUSTMENT_FACTOR = 0.2
    RATING_ADJUSTMENT_RANGE = 0.1
    VERSION_WEIGHTS = {
        StyleType.DIRECT: 1.2,
        StyleType.GENTLE: 1.1,
        StyleType.NEUTRAL: 1.0
    }
    STYLE_LEVEL_MIN = 1
    STYLE_LEVEL_MAX = 5
    
    def __init__(self, openai_service: OpenAIService):
        self.openai_service = openai_service
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def calculate_style_adjustment(self, 
                                       feedback_text: str, 
                                       rating: int, 
                                       selected_version: str) -> StyleAdjustment:
        """피드백을 통한 스타일 조정값 계산"""
        try:
            # OpenAI를 통한 피드백 분석
            style_deltas = await self.openai_service.analyze_style_feedback(feedback_text)
            
            # 조정 팩터 계산
            adjustment_factor = self._calculate_adjustment_factor(rating, selected_version)
            
            # StyleAdjustment 객체 생성
            base_adjustment = StyleAdjustment(
                formality_delta=style_deltas.get('formalityDelta', 0.0),
                friendliness_delta=style_deltas.get('friendlinessDelta', 0.0),
                emotion_delta=style_deltas.get('emotionDelta', 0.0),
                directness_delta=style_deltas.get('directnessDelta', 0.0)
            )
            
            return base_adjustment.apply_factor(adjustment_factor)
            
        except Exception as e:
            self.logger.error(f"스타일 조정값 계산 실패: {e}")
            return StyleAdjustment()  # 기본값 반환
    
    def _calculate_adjustment_factor(self, rating: int, selected_version: str) -> float:
        """평점과 선택된 버전에 따른 조정 팩터 계산"""
        # 평점 정규화 (1-5 -> -0.2 ~ +0.2)
        rating_factor = (rating - 3) * self.RATING_ADJUSTMENT_RANGE
        
        # 버전별 가중치
        try:
            style_type = StyleType(selected_version)
            version_weight = self.VERSION_WEIGHTS[style_type]
        except (ValueError, KeyError):
            version_weight = self.VERSION_WEIGHTS[StyleType.NEUTRAL]
        
        return self.BASE_ADJUSTMENT_FACTOR * (1 + rating_factor) * version_weight
    
    def apply_adjustment_to_profile(self, 
                                  current_profile: Dict[str, Any], 
                                  adjustment: StyleAdjustment) -> Dict[str, float]:
        """현재 프로필에 조정값 적용"""
        adjustments_map = {
            'sessionFormalityLevel': adjustment.formality_delta,
            'sessionFriendlinessLevel': adjustment.friendliness_delta,
            'sessionEmotionLevel': adjustment.emotion_delta,
            'sessionDirectnessLevel': adjustment.directness_delta
        }
        
        new_levels = {}
        for profile_key, delta in adjustments_map.items():
            current_level = current_profile.get(profile_key, 3)
            new_level = self._clamp_level(current_level + delta)
            new_levels[profile_key] = new_level
        
        return new_levels
    
    def _clamp_level(self, level: float) -> float:
        """레벨을 1-5 범위로 제한"""
        return max(self.STYLE_LEVEL_MIN, min(self.STYLE_LEVEL_MAX, level))


class UserPreferencesService(BaseService):
    """사용자 선호도 및 학습 관리 서비스"""
    
    def __init__(self, storage: DatabaseStorage, openai_service: OpenAIService):
        super().__init__()
        self.storage = storage
        self.openai_service = openai_service
        self.preference_extractor = PreferenceExtractor()
        self.learning_engine = StyleLearningEngine(openai_service)
    
    async def get_user_negative_preferences(self, user_id: str) -> NegativePreferences:
        """사용자 네거티브 프롬프트 선호도 조회"""
        try:
            # 데이터베이스에서 저장된 선호도 조회
            stored_prefs = await self.storage.get_negative_preferences(user_id)
            if stored_prefs:
                return NegativePreferences.from_dict(stored_prefs)
            
            # 사용자 프로필에서 추출
            user_profile = await self.storage.get_user_profile(user_id)
            if user_profile and user_profile.get('negativePromptPreferences'):
                return NegativePreferences.from_dict(user_profile['negativePromptPreferences'])
            
            # 프로필 기반 기본 선호도 생성
            return self.preference_extractor.extract_from_profile(user_profile)
            
        except Exception as e:
            self.logger.error(f"사용자 {user_id} 네거티브 선호도 조회 실패: {e}")
            return self.preference_extractor._get_default_preferences()
    
    async def save_user_negative_preferences(self, 
                                           user_id: str, 
                                           preferences: NegativePreferences) -> bool:
        """사용자 네거티브 프롬프트 선호도 저장"""
        try:
            # 데이터베이스에 저장
            success = await self.storage.save_negative_preferences(user_id, preferences.to_dict())
            if not success:
                raise Exception("데이터베이스 저장 실패")
            
            # 사용자 프로필에도 동기화
            await self._sync_preferences_to_profile(user_id, preferences)
            
            self.logger.info(f"사용자 {user_id} 네거티브 선호도 저장 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"사용자 {user_id} 네거티브 선호도 저장 실패: {e}")
            return False
    
    async def adapt_user_style(self, 
                             user_id: str, 
                             feedback_text: str,
                             rating: int,
                             selected_version: str) -> bool:
        """사용자 피드백을 통한 스타일 적응 학습"""
        try:
            # 입력 검증
            if not self._validate_feedback_input(feedback_text, rating, selected_version):
                return False
            
            # 스타일 조정값 계산
            adjustment = await self.learning_engine.calculate_style_adjustment(
                feedback_text, rating, selected_version
            )
            
            # 현재 프로필 조회
            current_profile = await self.storage.get_user_profile(user_id)
            if not current_profile:
                self.logger.warning(f"사용자 {user_id} 프로필을 찾을 수 없음")
                return False
            
            # 조정값 적용
            new_levels = self.learning_engine.apply_adjustment_to_profile(
                current_profile, adjustment
            )
            
            # 프로필 업데이트
            success = await self.storage.update_session_style(user_id, new_levels)
            
            if success:
                self.logger.info(f"사용자 {user_id} 스타일 학습 완료: {new_levels}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"사용자 {user_id} 스타일 적응 학습 실패: {e}")
            return False
    
    def _validate_feedback_input(self, 
                               feedback_text: str, 
                               rating: int, 
                               selected_version: str) -> bool:
        """피드백 입력 검증"""
        if not feedback_text or not feedback_text.strip():
            return False
        
        if not (1 <= rating <= 5):
            return False
        
        try:
            StyleType(selected_version)
            return True
        except ValueError:
            return False
    
    async def _sync_preferences_to_profile(self, 
                                         user_id: str, 
                                         preferences: NegativePreferences) -> bool:
        """선호도를 사용자 프로필에 동기화"""
        try:
            profile_update = {
                'negativePromptPreferences': preferences.to_dict()
            }
            
            success = await self.storage.update_user_profile(user_id, profile_update)
            if success:
                self.logger.debug(f"사용자 {user_id} 프로필에 선호도 동기화 완료")
            
            return success
            
        except Exception as e:
            self.logger.error(f"사용자 {user_id} 프로필 동기화 실패: {e}")
            return False