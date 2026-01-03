"""
RAG (Retrieval-Augmented Generation) 서비스
RAG Chain을 래핑하여 FastAPI와 연동하는 서비스 레이어
Facade 패턴으로 구현되어 실제 작업은 전문화된 모듈에 위임:
- RAGEmbedderManager: 임베더 초기화 및 관리
- RAGIngestionService: 문서 인덱싱
- RAGQueryService: 질의응답 처리
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger('chattoner')


class RAGService:
    """RAG를 활용한 문서 검색 및 질의응답 서비스 (Facade)"""

    def __init__(
        self,
        user_preferences_service=None,
        embedder_manager=None,
        ingestion_service=None,
        query_service=None
    ):
        """
        RAG 서비스 초기화 - 의존성 주입 방식

        Args:
            user_preferences_service: 사용자 선호도 서비스 (선택)
            embedder_manager: RAG 임베더 관리자 (주입 또는 자동 생성)
            ingestion_service: RAG 인덱싱 서비스 (주입 또는 자동 생성)
            query_service: RAG 질의응답 서비스 (주입 또는 자동 생성)
        """
        # RAG Chain 초기화 (LangChain 사용 시)
        self.rag_chain = None
        self._initialize_chain()

        # 전문화된 서비스 모듈 - 주입된 것 사용 또는 자동 생성
        if embedder_manager is not None:
            self.embedder_manager = embedder_manager
        else:
            # 하위 호환성: 주입되지 않은 경우 직접 생성
            from services.rag.rag_embedder_manager import RAGEmbedderManager
            self.embedder_manager = RAGEmbedderManager()

        if ingestion_service is not None:
            self.ingestion_service = ingestion_service
            # RAG Chain 업데이트
            self.ingestion_service.rag_chain = self.rag_chain
        else:
            # 하위 호환성: 주입되지 않은 경우 직접 생성
            from services.rag.rag_ingestion_service import RAGIngestionService
            self.ingestion_service = RAGIngestionService(rag_chain=self.rag_chain)

        if query_service is not None:
            self.query_service = query_service
            # RAG Chain 업데이트
            self.query_service.rag_chain = self.rag_chain
            # embedder_manager 업데이트
            self.query_service.embedder_manager = self.embedder_manager
        else:
            # 하위 호환성: 주입되지 않은 경우 직접 생성
            from services.rag.rag_query_service import RAGQueryService
            from services.prompt_engineering import PromptEngineer
            from services.openai_services import OpenAIService
            from services.conversion_service import ConversionService

            self.prompt_engineer = PromptEngineer()
            self.openai_service = OpenAIService()
            self.conversion_service = ConversionService()

            self.query_service = RAGQueryService(
                rag_chain=self.rag_chain,
                embedder_manager=self.embedder_manager,
                openai_service=self.openai_service,
                conversion_service=self.conversion_service,
                user_preferences_service=user_preferences_service
            )

        # 선택적 주입 (향후 확장용)
        self.user_preferences_service = user_preferences_service

        # 하위 호환성을 위한 속성 유지
        self.simple_embedder = self.embedder_manager.get_embedder()
        # query_service에서 사용하는 openai_service도 노출 (rag.py 엔드포인트에서 사용)
        if hasattr(self.query_service, 'openai_service'):
            self.openai_service = self.query_service.openai_service
    
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
    
    # ========== 문서 인덱싱 메서드 (RAGIngestionService에 위임) ==========
    
    def ingest_documents(self, folder_path: str) -> Dict[str, Any]:
        """
        문서 폴더에서 벡터 DB 생성
        
        Args:
            folder_path: 문서가 있는 폴더 경로
            
        Returns:
            처리 결과 딕셔너리
        """
        return self.ingestion_service.ingest_documents(folder_path)
    
    def ingest_company_documents(self, company_id: str, folder_path: str) -> Dict[str, Any]:
        """특정 기업용 문서를 인덱싱하여 기업 전용 벡터 스토어로 저장"""
        return self.ingestion_service.ingest_company_documents(company_id, folder_path)
    
    # ========== 질의응답 메서드 (RAGQueryService에 위임) ==========
    
    async def ask_question(self, 
                          query: str, 
                          context: Optional[str] = None,
                          company_id: Optional[str] = None) -> Dict[str, Any]:
        """
        단일 질의응답 (Simple Embedder 또는 RAG Chain 사용)
        
        Args:
            query: 질문
            context: 추가 컨텍스트
            company_id: 기업 ID
            
        Returns:
            질의응답 결과
        """
        return await self.query_service.ask_question(query, context, company_id)
    
    async def ask_generative_question(self, 
                                     query: str, 
                                     context: Optional[str] = None) -> Dict[str, Any]:
        """
        RAG Chain을 직접 사용하여 생성적인 답변을 얻는 메소드.
        (간단한 임베더 검색을 건너뜀)
        """
        return await self.query_service.ask_generative_question(query, context)
    
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
        return await self.query_service.ask_with_styles(query, user_profile, context)
    
    async def process_user_feedback(self,
                                   feedback_text: str,
                                   user_profile: Dict[str, Any],
                                   rating: Optional[int] = None,
                                   selected_version: str = "neutral") -> Dict[str, Any]:
        """
        사용자 피드백 처리 (ConversionService와 호환)
        """
        return await self.query_service.process_user_feedback(
            feedback_text, user_profile, rating, selected_version
        )
    
    # ========== 상태 조회 메서드 ==========
    
    def get_status(self) -> Dict[str, Any]:
        """RAG 서비스 상태 조회"""
        if not self.rag_chain:
            return {
                "rag_status": "not_initialized",
                "doc_count": 0,
                "services_available": False
            }
        
        return self.rag_chain.get_status()
