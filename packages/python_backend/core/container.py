"""
Dependency Injection Container
GitHub 기반 의존성 주입 컨테이너
"""

from dependency_injector import containers, providers
from .config import Settings, get_settings
from services.conversion_service import ConversionService
from services.prompt_engineering import PromptEngineer
from services.openai_services import OpenAIService
from services.user_preferences import UserPreferencesService
from services.document_service import DocumentService
from services.rag_service import RAGService
from services.rag.rag_embedder_manager import RAGEmbedderManager
from services.rag.rag_ingestion_service import RAGIngestionService
from services.rag.rag_query_service import RAGQueryService
from services.profile_generator import ProfileGeneratorService # Added import
from services.user_service import UserService
from services.pdf_summary_service import PDFSummaryService

# 선택적 import (의존성이 있을 때만)
try:
    from agents.quality_analysis_agent import OptimizedEnterpriseQualityAgent
    from services.enterprise_db_service import EnterpriseDBService, get_enterprise_db_service
    from services.quality_analysis_service import OptimizedEnterpriseQualityService
    ENTERPRISE_FEATURES_AVAILABLE = True
except ImportError as e:
    # @@ langgraph 의존성 설치 필요: pip install langgraph
    ENTERPRISE_FEATURES_AVAILABLE = False
    print(f"Enterprise features unavailable: {e}")
from database.storage import DatabaseStorage

class Container(containers.DeclarativeContainer):
    """의존성 주입 컨테이너"""
    
    # 설정
    config = providers.Configuration()
    
    # 설정 프로바이더
    settings = providers.Singleton(get_settings)
    
    # 코어 서비스들
    prompt_engineer = providers.Singleton(PromptEngineer)
    
    openai_service = providers.Singleton(
        OpenAIService,
        api_key=config.OPENAI_API_KEY,
        model=config.OPENAI_MODEL
    )

    # DatabaseStorage 싱글톤 인스턴스로 생성
    database_storage = providers.Singleton(DatabaseStorage)
    user_preferences_service = providers.Singleton(
        UserPreferencesService,
        storage=database_storage,
        openai_service=openai_service
    )
    
    # 메인 변환 서비스
    conversion_service = providers.Singleton(
        ConversionService,
        prompt_engineer=prompt_engineer,
        openai_service=openai_service
    )

    # 파인튜닝 서비스 제거됨 (finetune_service 미사용)

    # 문서 처리 서비스 (의존성 해결됨)
    document_service = providers.Singleton(
        DocumentService,
        openai_api_key=config.OPENAI_API_KEY
    )

    # RAG 전문화 서비스들 (싱글톤)
    rag_embedder_manager = providers.Singleton(RAGEmbedderManager)

    rag_ingestion_service = providers.Singleton(
        RAGIngestionService,
        rag_chain=None  # RAG Chain은 RAGService에서 초기화
    )

    rag_query_service = providers.Singleton(
        RAGQueryService,
        rag_chain=None,  # RAG Chain은 RAGService에서 초기화
        embedder_manager=rag_embedder_manager,
        openai_service=openai_service,
        conversion_service=conversion_service,
        user_preferences_service=user_preferences_service
    )

    # RAG 서비스 Facade (싱글톤으로 한번만 초기화)
    rag_service = providers.Singleton(
        RAGService,
        user_preferences_service=user_preferences_service,
        embedder_manager=rag_embedder_manager,
        ingestion_service=rag_ingestion_service,
        query_service=rag_query_service
    )

    # 프로필 생성 서비스 (OpenAIService 주입)
    profile_generator_service = providers.Singleton(
        ProfileGeneratorService,
        openai_service=openai_service
    )

    # PDF 요약 서비스 (OpenAIService 주입)
    pdf_summary_service = providers.Singleton(
        PDFSummaryService,
        openai_service=openai_service
    )

    # 기업용 기능들 (의존성이 있을 때만 활성화)
    if ENTERPRISE_FEATURES_AVAILABLE:
        # 기업 DB 서비스
        enterprise_db_service = providers.Singleton(EnterpriseDBService)

        # 기업용 품질분석 Agent (싱글톤으로 그래프 재사용)
        enterprise_quality_agent = providers.Singleton(
            OptimizedEnterpriseQualityAgent,
            rag_service=rag_service,
            db_service=enterprise_db_service
        )

        # 기업용 품질분석 서비스
        enterprise_quality_service = providers.Singleton(
            OptimizedEnterpriseQualityService,
            rag_service=rag_service
        )
