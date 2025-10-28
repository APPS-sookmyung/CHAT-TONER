"""
데이터베이스 스토리지 클래스
사용자 프로필, 변환 기록, 선호도 관리
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
import hashlib
import logging
from sqlalchemy.orm import Session
from .db import SessionLocal
from .models import (
    UserProfile, ConversionHistory,
    NegativePreferences, User, VectorDocumentMetadata, RAGQueryHistory
)

logger = logging.getLogger('chattoner.storage')

class DatabaseStorage:
    """데이터베이스 CRUD 작업을 위한 스토리지 클래스"""
    
    def __init__(self):
        self.session_factory = SessionLocal

    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """사용자 프로필 조회"""
        with self.session_factory() as db:
            try:
                # user_id를 문자열로 처리 (문자열 ID 허용)
                user_id_str = str(user_id)
                profile = db.query(UserProfile).filter(UserProfile.user_id == user_id_str).first()
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
                logger.error(f"사용자 프로필 조회 오류: {e}", exc_info=True)
                return None

    def save_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> bool:
        """사용자 프로필 저장"""
        with self.session_factory() as db:
            try:
                # user_id를 int로 변환
                user_id_str = str(user_id)

                # 기존 프로필 조회
                profile = db.query(UserProfile).filter(UserProfile.user_id == user_id_str).first()
                
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
                        user_id=user_id_str,
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
                logger.error(f"사용자 프로필 저장 오류: {e}", exc_info=True)
                return False

    def save_conversion(self, user_id: str, conversion_data: Dict[str, Any]) -> Optional[ConversionHistory]:
        """변환 기록 저장"""
        with self.session_factory() as db:
            try:
                user_id_str = str(user_id)
                conversion = ConversionHistory(
                    user_id=user_id_str,
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
                db.refresh(conversion)
                return conversion
                
            except Exception as e:
                db.rollback()
                logger.error(f"변환 기록 저장 오류: {e}", exc_info=True)
                return None

    def update_conversion_feedback(self, feedback_data: Dict[str, Any]) -> Optional[ConversionHistory]:
        """변환 기록에 피드백 업데이트"""
        with self.session_factory() as db:
            try:
                conversion_id = feedback_data.get('conversionId')
                if not conversion_id:
                    return None

                conversion = db.query(ConversionHistory).filter(ConversionHistory.id == conversion_id).first()
                
                if not conversion:
                    return None

                conversion.user_rating = feedback_data.get('rating')
                conversion.selected_version = feedback_data.get('selectedVersion')
                conversion.feedback_text = feedback_data.get('feedback_text')
                
                db.commit()
                db.refresh(conversion)
                return conversion

            except Exception as e:
                db.rollback()
                logger.error(f"피드백 업데이트 오류: {e}", exc_info=True)
                return None

    def get_conversion_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """사용자 변환 기록 조회"""
        with self.session_factory() as db:
            try:
                user_id_str = str(user_id)
                conversions = db.query(ConversionHistory)\
                    .filter(ConversionHistory.user_id == user_id_str)\
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
                logger.error(f"변환 기록 조회 오류: {e}", exc_info=True)
                return []

    def get_negative_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """사용자 네거티브 선호도 조회"""
        with self.session_factory() as db:
            try:
                user_id_str = str(user_id)
                prefs = db.query(NegativePreferences)\
                    .filter(NegativePreferences.user_id == user_id_str).first()
                
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
                logger.error(f"네거티브 선호도 조회 오류: {e}", exc_info=True)
                return None

    def save_negative_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """사용자 네거티브 선호도 저장"""
        with self.session_factory() as db:
            try:
                user_id_str = str(user_id)
                # 기존 선호도 조회
                prefs = db.query(NegativePreferences)\
                    .filter(NegativePreferences.user_id == user_id_str).first()
                
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
                        user_id=user_id_str,
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
                logger.error(f"네거티브 선호도 저장 오류: {e}", exc_info=True)
                return False

    # RAG 벡터 메타데이터 관련 메소드들
    def save_vector_document_metadata(self, metadata: Dict[str, Any]) -> bool:
        """벡터 문서 메타데이터 저장"""
        with self.session_factory() as db:
            try:
                # 문서 해시 생성
                content = f"{metadata['file_path']}{metadata['file_size_bytes']}{metadata.get('content_hash', '')}"
                document_hash = hashlib.sha256(content.encode()).hexdigest()

                # 기존 메타데이터 확인
                existing = db.query(VectorDocumentMetadata)\
                    .filter(VectorDocumentMetadata.document_hash == document_hash).first()

                if existing:
                    # 기존 메타데이터 업데이트
                    existing.last_accessed = datetime.utcnow()
                    existing.status = metadata.get('status', 'active')
                    existing.updated_at = datetime.utcnow()
                else:
                    # 새 메타데이터 생성
                    doc_metadata = VectorDocumentMetadata(
                        document_hash=document_hash,
                        file_name=metadata['file_name'],
                        file_path=metadata['file_path'],
                        file_size_bytes=metadata['file_size_bytes'],
                        content_type=metadata.get('content_type', 'text/plain'),
                        embedding_model=metadata['embedding_model'],
                        chunk_count=metadata['chunk_count'],
                        chunk_size=metadata['chunk_size'],
                        chunk_overlap=metadata['chunk_overlap'],
                        faiss_index_path=metadata['faiss_index_path'],
                        vector_dimension=metadata['vector_dimension'],
                        status=metadata.get('status', 'active')
                    )
                    db.add(doc_metadata)

                db.commit()
                return True

            except Exception as e:
                db.rollback()
                logger.error(f"벡터 문서 메타데이터 저장 오류: {e}", exc_info=True)
                return False

    def get_vector_document_metadata(self, document_hash: Optional[str] = None) -> List[Dict[str, Any]]:
        """벡터 문서 메타데이터 조회"""
        with self.session_factory() as db:
            try:
                query = db.query(VectorDocumentMetadata)

                if document_hash:
                    query = query.filter(VectorDocumentMetadata.document_hash == document_hash)

                query = query.filter(VectorDocumentMetadata.status == 'active')
                metadata_list = query.all()

                return [
                    {
                        "id": meta.id,
                        "document_hash": meta.document_hash,
                        "file_name": meta.file_name,
                        "file_path": meta.file_path,
                        "file_size_bytes": meta.file_size_bytes,
                        "content_type": meta.content_type,
                        "embedding_model": meta.embedding_model,
                        "chunk_count": meta.chunk_count,
                        "chunk_size": meta.chunk_size,
                        "chunk_overlap": meta.chunk_overlap,
                        "faiss_index_path": meta.faiss_index_path,
                        "vector_dimension": meta.vector_dimension,
                        "status": meta.status,
                        "last_accessed": meta.last_accessed.isoformat() if meta.last_accessed else None,
                        "created_at": meta.created_at.isoformat() if meta.created_at else None,
                        "updated_at": meta.updated_at.isoformat() if meta.updated_at else None
                    }
                    for meta in metadata_list
                ]

            except Exception as e:
                logger.error(f"벡터 문서 메타데이터 조회 오류: {e}", exc_info=True)
                return []

    def save_rag_query(self, user_id: str, query_data: Dict[str, Any]) -> bool:
        """RAG 질의 기록 저장"""
        with self.session_factory() as db:
            try:
                user_id_str = str(user_id)
                # 질의 해시 생성
                query_hash = hashlib.sha256(query_data['query_text'].encode()).hexdigest()

                rag_query = RAGQueryHistory(
                    user_id=user_id_str,
                    query_text=query_data['query_text'],
                    query_hash=query_hash,
                    context_type=query_data.get('context_type', 'general'),
                    retrieved_documents=query_data.get('retrieved_documents', []),
                    similarity_scores=query_data.get('similarity_scores', []),
                    total_search_time_ms=query_data.get('total_search_time_ms', 0),
                    generated_answer=query_data.get('generated_answer'),
                    answer_quality_score=query_data.get('answer_quality_score'),
                    model_used=query_data.get('model_used', 'gpt-4'),
                    total_generation_time_ms=query_data.get('total_generation_time_ms', 0),
                    user_rating=query_data.get('user_rating'),
                    user_feedback=query_data.get('user_feedback'),
                    was_helpful=query_data.get('was_helpful')
                )

                db.add(rag_query)
                db.commit()
                return True

            except Exception as e:
                db.rollback()
                logger.error(f"RAG 질의 기록 저장 오류: {e}", exc_info=True)
                return False

    def get_rag_query_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """RAG 질의 기록 조회"""
        with self.session_factory() as db:
            try:
                user_id_str = str(user_id)
                queries = db.query(RAGQueryHistory)\
                    .filter(RAGQueryHistory.user_id == user_id_str)\
                    .order_by(RAGQueryHistory.created_at.desc())\
                    .limit(limit).all()

                return [
                    {
                        "id": query.id,
                        "query_text": query.query_text,
                        "query_hash": query.query_hash,
                        "context_type": query.context_type,
                        "retrieved_documents": query.retrieved_documents,
                        "similarity_scores": query.similarity_scores,
                        "total_search_time_ms": query.total_search_time_ms,
                        "generated_answer": query.generated_answer,
                        "answer_quality_score": query.answer_quality_score,
                        "model_used": query.model_used,
                        "total_generation_time_ms": query.total_generation_time_ms,
                        "user_rating": query.user_rating,
                        "user_feedback": query.user_feedback,
                        "was_helpful": query.was_helpful,
                        "created_at": query.created_at.isoformat() if query.created_at else None
                    }
                    for query in queries
                ]

            except Exception as e:
                logger.error(f"RAG 질의 기록 조회 오류: {e}", exc_info=True)
                return []

    def update_vector_document_access(self, document_hash: str) -> bool:
        """벡터 문서 접근 시간 업데이트"""
        with self.session_factory() as db:
            try:
                metadata = db.query(VectorDocumentMetadata)\
                    .filter(VectorDocumentMetadata.document_hash == document_hash).first()

                if metadata:
                    metadata.last_accessed = datetime.utcnow()
                    db.commit()
                    return True

                return False

            except Exception as e:
                db.rollback()
                logger.error(f"벡터 문서 접근 시간 업데이트 오류: {e}", exc_info=True)
                return False