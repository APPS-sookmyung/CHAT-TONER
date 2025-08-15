"""
데이터베이스 스토리지 클래스
사용자 프로필, 변환 기록, 선호도 관리
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from .models import (
    SessionLocal, UserProfile, ConversionHistory, 
    NegativePreferences, User
)

class DatabaseStorage:
    """데이터베이스 CRUD 작업을 위한 스토리지 클래스"""
    
    def __init__(self):
        self.session_factory = SessionLocal

    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """사용자 프로필 조회"""
        with self.session_factory() as db:
            try:
                profile = db.query(UserProfile).filter(UserProfile.user_id == int(user_id)).first()
                if not profile:
                    return None
                
                return {
                    "userId": str(profile.user_id),
                    "baseFormalityLevel": profile.base_formality_level,
                    "baseFriendlinessLevel": profile.base_friendliness_level,
                    "baseEmotionLevel": profile.base_emotion_level,
                    "baseDirectnessLevel": profile.base_directness_level,
                    "sessionFormalityLevel": profile.session_formality_level,
                    "sessionFriendlinessLevel": profile.session_friendliness_level,
                    "sessionEmotionLevel": profile.session_emotion_level,
                    "sessionDirectnessLevel": profile.session_directness_level,
                    "questionnaireResponses": profile.questionnaire_responses or {},
                    "createdAt": profile.created_at.isoformat() if profile.created_at is not None else None,
                    "updatedAt": profile.updated_at.isoformat() if profile.updated_at is not None else None
                }
            except Exception as e:
                print(f"사용자 프로필 조회 오류: {e}")
                return None

    def save_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> bool:
        """사용자 프로필 저장"""
        with self.session_factory() as db:
            try:
                # 기존 프로필 조회
                profile = db.query(UserProfile).filter(UserProfile.user_id == int(user_id)).first()
                
                if profile:
                    # 기존 프로필 업데이트
                    profile.base_formality_level = profile_data.get('baseFormalityLevel', profile.base_formality_level)
                    profile.base_friendliness_level = profile_data.get('baseFriendlinessLevel', profile.base_friendliness_level)
                    profile.base_emotion_level = profile_data.get('baseEmotionLevel', profile.base_emotion_level)
                    profile.base_directness_level = profile_data.get('baseDirectnessLevel', profile.base_directness_level)
                    
                    # 세션 레벨 업데이트 (NULL 허용)
                    if 'sessionFormalityLevel' in profile_data:
                        profile.session_formality_level = profile_data['sessionFormalityLevel']
                    if 'sessionFriendlinessLevel' in profile_data:
                        profile.session_friendliness_level = profile_data['sessionFriendlinessLevel']
                    if 'sessionEmotionLevel' in profile_data:
                        profile.session_emotion_level = profile_data['sessionEmotionLevel']
                    if 'sessionDirectnessLevel' in profile_data:
                        profile.session_directness_level = profile_data['sessionDirectnessLevel']
                    
                    profile.questionnaire_responses = profile_data.get('questionnaireResponses', {})
                else:
                    # 새 프로필 생성
                    profile = UserProfile(
                        user_id=int(user_id),
                        base_formality_level=profile_data.get('baseFormalityLevel', 3),
                        base_friendliness_level=profile_data.get('baseFriendlinessLevel', 3),
                        base_emotion_level=profile_data.get('baseEmotionLevel', 3),
                        base_directness_level=profile_data.get('baseDirectnessLevel', 3),
                        session_formality_level=profile_data.get('sessionFormalityLevel'),
                        session_friendliness_level=profile_data.get('sessionFriendlinessLevel'),
                        session_emotion_level=profile_data.get('sessionEmotionLevel'),
                        session_directness_level=profile_data.get('sessionDirectnessLevel'),
                        questionnaire_responses=profile_data.get('questionnaireResponses', {})
                    )
                    db.add(profile)
                
                db.commit()
                return True
                
            except Exception as e:
                db.rollback()
                print(f"사용자 프로필 저장 오류: {e}")
                return False

    def save_conversion(self, user_id: str, conversion_data: Dict[str, Any]) -> bool:
        """변환 기록 저장"""
        with self.session_factory() as db:
            try:
                conversion = ConversionHistory(
                    user_id=int(user_id),
                    original_text=conversion_data.get('original_text', ''),
                    converted_texts=conversion_data.get('converted_texts', {}),
                    context=conversion_data.get('context', 'personal'),
                    user_rating=conversion_data.get('user_rating'),
                    selected_version=conversion_data.get('selected_version'),
                    feedback_text=conversion_data.get('feedback_text'),
                    sentiment_analysis=conversion_data.get('sentiment_analysis', {}),
                    prompts_used=conversion_data.get('prompts_used', {}),
                    model_used=conversion_data.get('model_used', 'gpt-4o')
                )
                
                db.add(conversion)
                db.commit()
                return True
                
            except Exception as e:
                db.rollback()
                print(f"변환 기록 저장 오류: {e}")
                return False

    def get_conversion_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """사용자 변환 기록 조회"""
        with self.session_factory() as db:
            try:
                conversions = db.query(ConversionHistory)\
                    .filter(ConversionHistory.user_id == int(user_id))\
                    .order_by(ConversionHistory.created_at.desc())\
                    .limit(limit).all()
                
                return [
                    {
                        "id": conv.id,
                        "original_text": conv.original_text,
                        "converted_texts": conv.converted_texts,
                        "context": conv.context,
                        "user_rating": conv.user_rating,
                        "selected_version": conv.selected_version,
                        "feedback_text": conv.feedback_text,
                        "sentiment_analysis": conv.sentiment_analysis,
                        "created_at": conv.created_at.isoformat() if conv.created_at is not None else None
                    }
                    for conv in conversions
                ]
                
            except Exception as e:
                print(f"변환 기록 조회 오류: {e}")
                return []

    def get_negative_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """사용자 네거티브 선호도 조회"""
        with self.session_factory() as db:
            try:
                prefs = db.query(NegativePreferences)\
                    .filter(NegativePreferences.user_id == int(user_id)).first()
                
                if not prefs:
                    return None
                
                return {
                    "user_id": str(prefs.user_id),
                    "avoidFloweryLanguage": prefs.avoid_flowery_language,
                    "avoidRepetitiveWords": prefs.avoid_repetitive_words,
                    "commaUsageStyle": prefs.comma_usage_style,
                    "contentOverFormat": prefs.content_over_format,
                    "bulletPointUsage": prefs.bullet_point_usage,
                    "emoticonUsage": prefs.emoticon_usage,
                    "customNegativePrompts": prefs.custom_negative_prompts if prefs.custom_negative_prompts is not None else []
                }
                
            except Exception as e:
                print(f"네거티브 선호도 조회 오류: {e}")
                return None

    def save_negative_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """사용자 네거티브 선호도 저장"""
        with self.session_factory() as db:
            try:
                # 기존 선호도 조회
                prefs = db.query(NegativePreferences)\
                    .filter(NegativePreferences.user_id == int(user_id)).first()
                
                if prefs:
                    # 기존 선호도 업데이트
                    prefs.avoid_flowery_language = preferences.get('avoidFloweryLanguage', prefs.avoid_flowery_language)
                    prefs.avoid_repetitive_words = preferences.get('avoidRepetitiveWords', prefs.avoid_repetitive_words)
                    prefs.comma_usage_style = preferences.get('commaUsageStyle', prefs.comma_usage_style)
                    prefs.content_over_format = preferences.get('contentOverFormat', prefs.content_over_format)
                    prefs.bullet_point_usage = preferences.get('bulletPointUsage', prefs.bullet_point_usage)
                    prefs.emoticon_usage = preferences.get('emoticonUsage', prefs.emoticon_usage)
                    prefs.custom_negative_prompts = preferences.get('customNegativePrompts', [])
                    # updated_at은 자동으로 SQLAlchemy에서 처리됨
                else:
                    # 새 선호도 생성
                    prefs = NegativePreferences(
                        user_id=int(user_id),
                        avoid_flowery_language=preferences.get('avoidFloweryLanguage', 'moderate'),
                        avoid_repetitive_words=preferences.get('avoidRepetitiveWords', 'moderate'),
                        comma_usage_style=preferences.get('commaUsageStyle', 'moderate'),
                        content_over_format=preferences.get('contentOverFormat', 'moderate'),
                        bullet_point_usage=preferences.get('bulletPointUsage', 'moderate'),
                        emoticon_usage=preferences.get('emoticonUsage', 'strict'),
                        custom_negative_prompts=preferences.get('customNegativePrompts', [])
                    )
                    db.add(prefs)
                
                db.commit()
                return True
                
            except Exception as e:
                db.rollback()
                print(f"네거티브 선호도 저장 오류: {e}")
                return False