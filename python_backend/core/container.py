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
# from services.document_service import DocumentService  # pypdf 의존성 문제로 주석 처리
from services.rag_service import RAGService

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

    # RAG 서비스 (싱글톤으로 한번만 초기화)
    rag_service = providers.Singleton(RAGService)

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
