"""
pytest 설정 파일 - 공통 픽스처와 설정
RAG 테스트를 위한 FastAPI, PostgreSQL, pgvector 설정
"""

import pytest
import asyncio
import os
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from httpx import AsyncClient
from unittest.mock import Mock, patch

# FastAPI 앱 임포트
from main import create_app

# 테스트 환경 변수 설정
os.environ["TESTING"] = "true"
os.environ["DEBUG"] = "false"


@pytest.fixture(scope="session")
def event_loop():
    """세션 범위의 이벤트 루프"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def app():
    """FastAPI 애플리케이션 픽스처"""
    return create_app()


@pytest.fixture
def client(app):
    """동기 테스트 클라이언트"""
    return TestClient(app)


@pytest.fixture
async def async_client(app) -> AsyncGenerator[AsyncClient, None]:
    """비동기 테스트 클라이언트"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_openai_client():
    """OpenAI 클라이언트 모킹"""
    with patch("openai.OpenAI") as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        
        # 채팅 완료 응답 모킹
        mock_instance.chat.completions.create.return_value = Mock(
            choices=[Mock(
                message=Mock(content="테스트 응답입니다.")
            )]
        )
        
        # 임베딩 응답 모킹
        mock_instance.embeddings.create.return_value = Mock(
            data=[Mock(embedding=[0.1] * 1536)]
        )
        
        yield mock_instance


@pytest.fixture
def mock_rag_service():
    """RAG 서비스 모킹"""
    with patch("services.rag_service.RAGService") as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        
        # 기본 응답 설정
        mock_instance.get_status.return_value = {
            "rag_status": "ready",
            "doc_count": 5,
            "services_available": True
        }
        
        mock_instance.ingest_documents.return_value = {
            "success": True,
            "documents_processed": 5,
            "error": None
        }
        
        mock_instance.ask_question.return_value = {
            "success": True,
            "answer": "테스트 RAG 응답입니다.",
            "sources": [{"source": "test_doc.txt"}],
            "metadata": {}
        }
        
        mock_instance.ask_with_styles.return_value = {
            "success": True,
            "converted_texts": {
                "formal": "공식적인 톤의 응답입니다.",
                "casual": "편안한 톤의 응답이에요.",
                "professional": "전문적인 톤의 응답입니다."
            },
            "sources": [{"source": "test_doc.txt"}],
            "rag_context": "테스트 컨텍스트",
            "metadata": {}
        }
        
        yield mock_instance


@pytest.fixture
def mock_container():
    """의존성 주입 컨테이너 모킹"""
    with patch("core.container.Container") as mock:
        container_instance = Mock()
        mock.return_value = container_instance
        
        # 설정 모킹
        container_instance.config.from_dict.return_value = None
        
        yield container_instance


@pytest.fixture
def test_user_profile():
    """테스트용 사용자 프로필"""
    return {
        "baseFormalityLevel": 3,
        "baseFriendlinessLevel": 4,
        "baseEmotionLevel": 3,
        "baseDirectnessLevel": 3
    }


@pytest.fixture
def sample_documents():
    """테스트용 문서 데이터"""
    return [
        {
            "filename": "business_style.txt",
            "content": "비즈니스 스타일 가이드입니다."
        },
        {
            "filename": "grammar_rules.txt", 
            "content": "문법 규칙에 대한 내용입니다."
        }
    ]


# PostgreSQL + pgvector 테스트 픽스처들
@pytest.fixture(scope="session")
def test_db_url():
    """테스트 데이터베이스 URL"""
    return "postgresql://test:test@localhost:5432/chattoner_test"


@pytest.fixture
def mock_vector_store():
    """벡터 스토어 모킹 (pgvector 대신)"""
    with patch("langchain_community.vectorstores.FAISS") as mock:
        mock_instance = Mock()
        mock.load_local.return_value = mock_instance
        
        # 벡터 검색 결과 모킹
        mock_instance.as_retriever.return_value.invoke.return_value = [
            Mock(
                page_content="테스트 문서 내용입니다.",
                metadata={"source": "test_doc.txt"}
            )
        ]
        
        mock_instance.index.ntotal = 100
        mock_instance.index.d = 1536
        
        yield mock_instance


@pytest.fixture(autouse=True)
def setup_test_environment():
    """모든 테스트 실행 전 환경 설정"""
    # 테스트 모드 설정
    os.environ["TESTING"] = "true"
    os.environ["DEBUG"] = "false"
    
    yield
    
    # 테스트 후 정리 (필요시)
    pass


# 마커 기반 픽스처들
@pytest.fixture
def integration_setup():
    """통합 테스트용 설정"""
    # 실제 서비스 연동 테스트시 사용
    pass


@pytest.fixture  
def unit_setup():
    """단위 테스트용 설정"""
    # 모든 외부 의존성 모킹
    pass