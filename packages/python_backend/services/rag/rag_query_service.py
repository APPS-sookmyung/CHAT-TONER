"""
RAG Query Service
질의응답 및 검색 처리를 담당하는 모듈
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from core.rag_config import get_rag_config
from utils.response_helpers import create_error_response

logger = logging.getLogger('chattoner.rag.query')


class RAGQueryService:
    """RAG 기반 질의응답 및 검색 처리"""
    
    def __init__(
        self,
        rag_chain=None,
        embedder_manager=None,
        openai_service=None,
        conversion_service=None,
        user_preferences_service=None
    ):
        """
        질의응답 서비스 초기화
        
        Args:
            rag_chain: RAG Chain 인스턴스
            embedder_manager: 임베더 매니저 인스턴스
            openai_service: OpenAI 서비스 인스턴스
            conversion_service: 변환 서비스 인스턴스
            user_preferences_service: 사용자 선호도 서비스 인스턴스
        """
        self.rag_chain = rag_chain
        self.embedder_manager = embedder_manager
        self.openai_service = openai_service
        self.conversion_service = conversion_service
        self.user_preferences_service = user_preferences_service
    
    def _get_timestamp(self):
        """현재 타임스탬프 반환"""
        return datetime.now().isoformat()

    async def ask_question(self, 
                          query: str, 
                          context: Optional[str] = None,
                          company_id: Optional[str] = None) -> Dict[str, Any]:
        """
        단일 질의응답 (Simple Embedder 또는 RAG Chain 사용)
        
        Args:
            query: 질문
            context: 추가 컨텍스트
            
        Returns:
            질의응답 결과
        """
        base_metadata = {
            "query_timestamp": self._get_timestamp(),
            "query_type": "document_search",
            "query_length": len(query),
            "context_provided": bool(context)
        }
        
        try:
            logger.info(f"단일 질의응답 요청: {len(query)}자, context={bool(context)}")
            
            # 입력 검증
            if not query.strip():
                return create_error_response(
                    "빈 질문은 처리할 수 없습니다.",
                    answer="",
                    original_query=query,
                    context=context,
                    sources=[],
                    metadata={
                        **base_metadata,
                        "model_used": "none",
                        "error_type": "service_unavailable"
                    }
                )
            
            # GPT/Simple Embedder 우선 사용
            result = await self._try_embedder_search(query, context, base_metadata)
            if result:
                return result
            
            # RAG Chain 백업 사용 (기업별 인덱스 우선 적용)
            if self.rag_chain and company_id:
                try:
                    from langchain_pipeline.retriever.vector_db import load_vector_store
                    cfg = get_rag_config()
                    company_index_path = Path(cfg.faiss_index_path) / company_id
                    vs = load_vector_store(company_index_path)
                    if vs:
                        logger.info(f"기업 전용 벡터스토어 사용: {company_index_path}")
                        retriever = vs.as_retriever(search_kwargs={"k": 5})
                        # ask_with_retriever를 직접 호출하여 race condition 방지
                        result = self.rag_chain.ask_with_retriever(query, context, retriever)
                        if result and result.get("success"):
                            result["original_query"] = query
                            result["context"] = context
                            result["metadata"] = {
                                **base_metadata,
                                "model_used": "rag_chain_company_specific",
                            }
                            return result
                except Exception as e:
                    logger.warning(f"기업 전용 벡터스토어 로드 실패(기본 인덱스로 진행): {e}")

            result = await self._try_rag_chain(query, context, base_metadata)
            if result:
                return result
            
            # 모든 방법 실패
            return create_error_response(
                "RAG 서비스가 초기화되지 않았습니다.",
                answer="",
                original_query=query,
                context=context,
                sources=[],
                metadata={
                    **base_metadata,
                    "model_used": "none",
                    "error_type": "service_unavailable"
                }
            )
            
        except Exception as e:
            logger.exception("단일 질의응답 중 오류")
            return create_error_response(
                f"질의응답 중 서버 오류가 발생했습니다: {e!s}",
                answer="",
                original_query=query,
                context=context,
                sources=[],
                metadata={
                    **base_metadata,
                    "model_used": "none",
                    "error_type": "service_unavailable"
                }
            )
    
    async def ask_generative_question(self, 
                                     query: str, 
                                     context: Optional[str] = None) -> Dict[str, Any]:
        """
        RAG Chain을 직접 사용하여 생성적인 답변을 얻는 메소드.
        (간단한 임베더 검색을 건너뜀)
        """
        base_metadata = {
            "query_timestamp": self._get_timestamp(),
            "query_type": "generative_rag",
            "context_provided": bool(context)
        }
        
        try:
            logger.info(f"생성형 RAG 요청: {len(query)}자, context={bool(context)}")

            if not query.strip():
                return create_error_response(
                    "빈 질문은 처리할 수 없습니다.",
                    answer="",
                    original_query=query,
                    context=context,
                    sources=[],
                    metadata={
                        **base_metadata,
                        "model_used": "none",
                        "error_type": "service_unavailable"
                    }
                )
            
            # RAG Chain을 직접 호출
            result = await self._try_rag_chain(query, context, base_metadata)
            if result:
                return result
            
            # RAG Chain 실패
            return create_error_response(
                "RAG 서비스가 초기화되지 않았거나 답변 생성에 실패했습니다.",
                answer="",
                original_query=query,
                context=context,
                sources=[],
                metadata={
                    **base_metadata,
                    "model_used": "none",
                    "error_type": "service_unavailable"
                }
            )

        except Exception as e:
            logger.error(f"생성형 RAG 중 오류: {e}")
            return create_error_response(
                f"생성형 RAG 중 서버 오류가 발생했습니다: {str(e)}",
                answer="",
                original_query=query,
                context=context,
                sources=[],
                metadata={
                    **base_metadata,
                    "model_used": "none",
                    "error_type": "service_unavailable"
                }
            )
    
    async def _try_embedder_search(self, query: str, context: Optional[str], base_metadata: dict) -> Optional[Dict[str, Any]]:
        """임베더 검색 시도"""
        if not self.embedder_manager or not self.embedder_manager.is_available():
            return None

        simple_embedder = self.embedder_manager.get_embedder()
        if not simple_embedder:
            return None

        try:
            search_results = simple_embedder.search(query, top_k=3)
            
            if not search_results:
                logger.warning("임베더 검색 결과 없음")
                return None
            
            # 검색 결과를 답변으로 구성
            best_match = search_results[0]
            answer = f"관련 정보를 찾았습니다:\n\n{best_match[0][:300]}..."
            
            # 임베딩 모델 타입 확인
            from langchain_pipeline.embedder.gpt_embedder import GPTTextEmbedder
            model_type = "gpt_embedder" if isinstance(simple_embedder, GPTTextEmbedder) else "simple_embedder"
            
            sources = [
                {
                    "content": doc[:100] + "..." if len(doc) > 100 else doc,
                    "similarity": f"{score:.3f}",
                    "source": f"{'GPT' if model_type == 'gpt_embedder' else 'TF-IDF'} 기반 검색",
                    "rank": i + 1
                }
                for i, (doc, score) in enumerate(search_results)
            ]
            
            return {
                "success": True,
                "answer": answer,
                "original_query": query,
                "context": context,
                "sources": sources,
                "metadata": {
                    **base_metadata,
                    "model_used": model_type,
                    "search_results_count": len(search_results),
                    "best_similarity": f"{search_results[0][1]:.3f}"
                }
            }
            
        except Exception as e:
            logger.error(f"임베더 검색 오류: {e}")
            return None
    
    async def _try_rag_chain(self, query: str, context: Optional[str], base_metadata: dict) -> Optional[Dict[str, Any]]:
        """RAG Chain 검색 시도"""
        if not self.rag_chain:
            return None
            
        try:
            result = self.rag_chain.ask(query, context)
            
            return {
                "success": result.get("success", False),
                "answer": result.get("answer", ""),
                "original_query": query,
                "context": context,
                "sources": result.get("sources", []),
                "error": result.get("error", "알 수 없는 오류") if not result.get("success") else None,
                "metadata": {
                    **base_metadata,
                    "model_used": "rag_chain",
                    "query_type": "single_answer",
                    "rag_timestamp": result.get("timestamp")
                }
            }
            
        except Exception as e:
            logger.error(f"RAG Chain 오류: {e}")
            return None

    async def ask_with_styles(self, 
                             query: str, 
                             user_profile: Dict[str, Any], 
                             context: str = "personal") -> Dict[str, Any]:
        """
        3가지 스타일로 질의응답 (ConversionService와 동일한 구조)
        
        Args:
            query: 질문
            user_profile: 사용자 프로필
            context: 변환 컨텍스트
            
        Returns:
            3가지 스타일 변환 결과
        """
        if not self.rag_chain:
            return {
                "success": False,
                "error": "RAG 서비스가 초기화되지 않았습니다.",
                "original_query": query,
                "converted_texts": {
                    "direct": "",
                    "gentle": "",
                    "neutral": ""
                },
                "sources": [],
                "metadata": {
                    "query_timestamp": self._get_timestamp(),
                    "model_used": "none"
                }
            }
        
        try:
            logger.info(f"스타일별 질의응답 요청: {len(query)}자, context={context}")
            
            result = await self.rag_chain.ask_with_styles(
                query=query,
                user_profile=user_profile,
                context=context
            )
            
            # ConversionService와 호환되는 형태로 결과 구성
            if result.get("success"):
                formatted_result = {
                    "success": True,
                    "original_query": query,
                    "converted_texts": result.get("converted_texts", {}),
                    "context": context,
                    "user_profile": user_profile,
                    "sources": result.get("sources", []),
                    "rag_context": result.get("rag_context", ""),
                    "sentiment_analysis": result.get("sentiment_analysis", {}),
                    "metadata": {
                        "prompts_used": result.get("metadata", {}).get("prompts_used", ["rag_conversion"]),
                        "query_timestamp": self._get_timestamp(),
                        "model_used": "gpt-4o + faiss",
                        "query_type": "style_conversion"
                    }
                }
            else:
                formatted_result = {
                    "success": False,
                    "error": result.get("error", "스타일 변환 실패"),
                    "original_query": query,
                    "converted_texts": result.get("converted_texts", {
                        "direct": "",
                        "gentle": "",
                        "neutral": ""
                    }),
                    "context": context,
                    "user_profile": user_profile,
                    "sources": [],
                    "metadata": {
                        "query_timestamp": self._get_timestamp(),
                        "model_used": "none"
                    }
                }
            
            return formatted_result
            
        except Exception as e:
            logger.error(f"스타일별 질의응답 중 오류: {e}")
            return {
                "success": False,
                "error": f"스타일 변환 중 서버 오류가 발생했습니다: {str(e)}",
                "original_query": query,
                "converted_texts": {
                    "direct": "",
                    "gentle": "",
                    "neutral": ""
                },
                "context": context,
                "user_profile": user_profile,
                "sources": [],
                "metadata": {
                    "query_timestamp": self._get_timestamp(),
                    "model_used": "none"
                }
            }
    
    async def process_user_feedback(self,
                                   feedback_text: str,
                                   user_profile: Dict[str, Any],
                                   rating: Optional[int] = None,
                                   selected_version: str = "neutral") -> Dict[str, Any]:
        """
        사용자 피드백 처리 (ConversionService와 호환)
        """
        try:
            if self.user_preferences_service and rating:
                # UserPreferencesService를 통한 고급 피드백 처리
                user_id = user_profile.get('userId', 'unknown')
                success = await self.user_preferences_service.adapt_user_style(
                    user_id=user_id,
                    feedback_text=feedback_text,
                    rating=rating,
                    selected_version=selected_version
                )
                
                if success:
                    updated_profile = user_profile.copy()
                    return {
                        "success": True,
                        "updated_profile": updated_profile,
                        "style_adjustments": {"advanced_learning": True},
                        "feedback_processed": feedback_text
                    }
            
            # 기본 피드백 처리 (OpenAIService 사용) - ConversionService 로직
            if not self.openai_service:
                return create_error_response(
                    "OpenAI 서비스가 초기화되지 않았습니다.",
                    updated_profile=user_profile
                )
            style_deltas = await self.openai_service.analyze_style_feedback(feedback_text)
            
            updated_profile = user_profile.copy()
            
            current_formality = updated_profile.get('sessionFormalityLevel', 
                                                  updated_profile.get('baseFormalityLevel', 3))
            current_friendliness = updated_profile.get('sessionFriendlinessLevel',
                                                     updated_profile.get('baseFriendlinessLevel', 3))
            current_emotion = updated_profile.get('sessionEmotionLevel',
                                                updated_profile.get('baseEmotionLevel', 3))
            current_directness = updated_profile.get('sessionDirectnessLevel',
                                                   updated_profile.get('baseDirectnessLevel', 3))
            
            updated_profile['sessionFormalityLevel'] = max(1, min(5, 
                current_formality + style_deltas.get('formalityDelta', 0) * 2))
            updated_profile['sessionFriendlinessLevel'] = max(1, min(5,
                current_friendliness + style_deltas.get('friendlinessDelta', 0) * 2))
            updated_profile['sessionEmotionLevel'] = max(1, min(5,
                current_emotion + style_deltas.get('emotionDelta', 0) * 2))
            updated_profile['sessionDirectnessLevel'] = max(1, min(5,
                current_directness + style_deltas.get('directnessDelta', 0) * 2))
            
            return {
                "success": True,
                "updated_profile": updated_profile,
                "style_adjustments": style_deltas,
                "feedback_processed": feedback_text
            }
            
        except Exception as e:
            logger.error(f"피드백 처리 오류: {e}")
            return {
                "success": False,
                "error": str(e),
                "updated_profile": user_profile
            }
