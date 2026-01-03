"""
RAG (Retrieval-Augmented Generation) 서비스
RAG Chain을 래핑하여 FastAPI와 연동하는 서비스 레이어
ConversionService와 동일한 패턴으로 구현
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path
from core.rag_config import get_rag_config
from datetime import datetime
from utils.response_helpers import create_error_response

logger = logging.getLogger('chattoner')

class RAGService:
    """RAG를 활용한 문서 검색 및 질의응답 서비스"""
    
    def __init__(self, user_preferences_service=None):
        """RAG 서비스 초기화 - ConversionService와 동일한 패턴"""
        # 직접 생성 (ConversionService 패턴)
        from services.prompt_engineering import PromptEngineer
        from services.openai_services import OpenAIService
        from services.conversion_service import ConversionService
        
        self.prompt_engineer = PromptEngineer()
        self.openai_service = OpenAIService()
        self.conversion_service = ConversionService()
        
        # 선택적 주입 (향후 확장용)
        self.user_preferences_service = user_preferences_service
        
        # Simple Embedder 초기화
        self.simple_embedder = None
        self._initialize_simple_embedder()
        
        # RAG Chain 초기화 (LangChain 사용 시)
        self.rag_chain = None
        self._initialize_chain()
    
    def _initialize_simple_embedder(self):
        """GPT 및 Simple Text Embedder 초기화 (개선된 버전)"""
        # @@ [윤지원] 기업 특화 임베딩 부족: 기업별 지식베이스, 가이드라인 문서 처리 로직 없음
        embedder_initialized = False

        # GPT Embedder 우선 시도
        if self._try_gpt_embedder():
            embedder_initialized = True

        # 실패 시 Simple Embedder 백업
        if not embedder_initialized:
            self._try_simple_embedder()
    
    def _try_gpt_embedder(self) -> bool:
        """GPT Embedder 초기화 시도"""
        try:
            from langchain_pipeline.embedder.gpt_embedder import GPTTextEmbedder
            gpt_embedder = GPTTextEmbedder()
            
            if not gpt_embedder.is_available():
                logger.warning("OpenAI API 사용 불가 - Simple Embedder로 전환")
                return False
            
            # 기존 임베딩 로드 시도
            if gpt_embedder.load():
                logger.info("GPT Text Embedder 로드 완료")
                self.simple_embedder = gpt_embedder
                return True
            
            # 새로 생성
            documents = self._load_documents()
            if documents and gpt_embedder.fit(documents) and gpt_embedder.save():
                logger.info("GPT 임베딩 생성 및 저장 완료")
                self.simple_embedder = gpt_embedder
                return True
                
            logger.warning("GPT 임베딩 생성 실패")
            return False
            
        except Exception as e:
            logger.warning(f"GPT Embedder 초기화 실패: {e}")
            return False
    
    def _try_simple_embedder(self):
        """Simple Embedder 백업 초기화"""
        try:
            from langchain_pipeline.embedder.simple_embedder import SimpleTextEmbedder, create_embeddings_from_documents
            from pathlib import Path
            
            self.simple_embedder = SimpleTextEmbedder()
            
            if self.simple_embedder.load():
                logger.info("Simple Text Embedder 로드 완료 (백업)")
                return
            
            # 새로 생성
            cfg = get_rag_config()
            docs_path = Path(cfg.documents_path)
            if create_embeddings_from_documents(docs_path) and self.simple_embedder.load():
                logger.info("Simple Text Embedder 생성 및 로드 완료")
            else:
                logger.error("Simple Text Embedder 초기화 완전 실패")
                self.simple_embedder = None
                
        except Exception as e:
            logger.error(f"Simple Text Embedder 초기화 실패: {e}")
            self.simple_embedder = None
    
    def _load_documents(self) -> list:
        """문서 로드 공통 함수"""
        from pathlib import Path
        cfg = get_rag_config()
        docs_path = Path(cfg.documents_path)
        documents = []
        
        if not docs_path.exists():
            logger.warning(f"문서 폴더가 존재하지 않음: {docs_path}")
            return documents
        
        for txt_file in docs_path.glob("*.txt"):
            try:
                content = txt_file.read_text(encoding='utf-8')
                if content.strip():  # 빈 파일 제외
                    documents.append(content)
            except Exception as e:
                logger.warning(f"문서 로드 실패 {txt_file}: {e}")
                
        logger.info(f"총 {len(documents)}개 문서 로드됨")
        return documents

    def _initialize_chain(self):
        """RAG Chain 초기화 (LangChain 사용 시)"""
        try:
            from langchain_pipeline.chains.rag_chain import RAGChain
            # RAG Chain에 서비스들 전달
            self.rag_chain = RAGChain()
            logger.info("RAG Chain 초기화 완료")
        except ImportError as e:
            logger.warning(f"RAG Chain import 실패 (LangChain 없음): {e}")
            self.rag_chain = None
        except Exception as e:
            logger.error(f"RAG Chain 초기화 실패: {e}")
            self.rag_chain = None
    
    def _get_timestamp(self):
        """현재 타임스탬프 반환"""
        return datetime.now().isoformat()
    
    def ingest_documents(self, folder_path: str) -> Dict[str, Any]:
        """
        문서 폴더에서 벡터 DB 생성
        
        Args:
            folder_path: 문서가 있는 폴더 경로
            
        Returns:
            처리 결과 딕셔너리
        """
        if not self.rag_chain:
            return {
                "success": False,
                "error": "RAG 서비스가 초기화되지 않았습니다.",
                "documents_processed": 0
            }
        
        try:
            logger.info(f"문서 인덱싱 요청: {folder_path}")
            
            result = self.rag_chain.ingest_documents(folder_path)
            
            if result.get("success"):
                logger.info(f"문서 인덱싱 완료: {result.get('documents_processed', 0)}개 처리")
            else:
                logger.error(f"문서 인덱싱 실패: {result.get('error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"문서 인덱싱 중 오류: {e}")
            return {
                "success": False,
                "error": f"문서 인덱싱 중 서버 오류가 발생했습니다: {str(e)}",
                "documents_processed": 0
            }

    def ingest_company_documents(self, company_id: str, folder_path: str) -> Dict[str, Any]:
        """특정 기업용 문서를 인덱싱하여 기업 전용 벡터 스토어로 저장"""
        try:
            from langchain_pipeline.retriever.vector_db import ingest_documents_from_folder
            cfg = get_rag_config()
            company_index_path = Path(cfg.faiss_index_path) / company_id
            company_index_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"기업 인덱싱 요청: company={company_id}, folder={folder_path}, index={company_index_path}")

            vectorstore, docs = ingest_documents_from_folder(Path(folder_path), save_path=company_index_path)
            if vectorstore is not None:
                # 기업 전용 벡터 스토어 재적용(체인 사용 시)
                if self.rag_chain:
                    try:
                        self.rag_chain.vectorstore = vectorstore
                        self.rag_chain.retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
                        self.rag_chain.is_initialized = True
                    except Exception as e:
                        logger.warning(f"RAGChain에 기업 벡터스토어 적용 실패: {e}")
                return {"success": True, "documents_processed": len(docs)}
            return {"success": False, "error": "문서 처리 실패", "documents_processed": 0}
        except Exception as e:
            logger.error(f"기업 문서 인덱싱 중 오류: {e}")
            return {"success": False, "error": str(e), "documents_processed": 0}
    
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
                        self.rag_chain.vectorstore = vs
                        self.rag_chain.retriever = vs.as_retriever(search_kwargs={"k": 5})
                        self.rag_chain.is_initialized = True
                        logger.info(f"기업 전용 벡터스토어 사용: {company_index_path}")
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
            logger.error(f"단일 질의응답 중 오류: {e}")
            return create_error_response(
                f"질의응답 중 서버 오류가 발생했습니다: {str(e)}",
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
        if not self.simple_embedder:
            return None
            
        try:
            search_results = self.simple_embedder.search(query, top_k=3)
            
            if not search_results:
                logger.warning("임베더 검색 결과 없음")
                return None
            
            # 검색 결과를 답변으로 구성
            best_match = search_results[0]
            answer = f"관련 정보를 찾았습니다:\n\n{best_match[0][:300]}..."
            
            # 임베딩 모델 타입 확인
            from langchain_pipeline.embedder.gpt_embedder import GPTTextEmbedder
            model_type = "gpt_embedder" if isinstance(self.simple_embedder, GPTTextEmbedder) else "simple_embedder"
            
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
            style_deltas = self.openai_service.analyze_style_feedback(feedback_text)
            
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
    
    def get_status(self) -> Dict[str, Any]:
        """RAG 서비스 상태 조회"""
        if not self.rag_chain:
            return {
                "rag_status": "not_initialized",
                "doc_count": 0,
                "services_available": False
            }
        
        return self.rag_chain.get_status()
