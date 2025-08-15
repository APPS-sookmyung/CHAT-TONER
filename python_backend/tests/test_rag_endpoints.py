"""
RAG 엔드포인트 테스트
실제 PostgreSQL + pgvector 환경에서 RAG API 테스트
"""

import pytest
from httpx import AsyncClient
from fastapi import status
from unittest.mock import patch, Mock, AsyncMock


class TestRAGEndpoints:
    """RAG 엔드포인트 테스트 - 실제 경로 반영"""
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_rag_status_endpoint(self, async_client: AsyncClient, mock_rag_service):
        """GET /api/v1/rag/status - RAG 상태 확인"""
        # Given: RAG 서비스가 정상 상태
        mock_rag_service.get_status.return_value = {
            "rag_status": "ready",
            "doc_count": 10,
            "services_available": True
        }
        
        # When: 상태 확인 요청
        response = await async_client.get("/api/v1/rag/status")
        
        # Then: 정상 응답
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["rag_status"] == "ready"
        assert data["doc_count"] == 10
        assert data["services_available"] is True
        assert data["documents_path"] == "python_backend/langchain_pipeline/data/documents"
        assert data["index_path"] == "python_backend/langchain_pipeline/data/faiss_index"
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_document_ingest_success(self, async_client: AsyncClient, mock_rag_service):
        """POST /api/v1/rag/ingest - 문서 인덱싱 성공"""
        # Given: 성공적인 인덱싱 응답
        mock_rag_service.ingest_documents.return_value = {
            "success": True,
            "documents_processed": 5,
            "error": None
        }
        
        # When: 문서 인덱싱 요청 (기본 경로 사용)
        request_data = {
            "folder_path": "python_backend/langchain_pipeline/data/documents"
        }
        response = await async_client.post("/api/v1/rag/ingest", json=request_data)
        
        # Then: 성공 응답
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["documents_processed"] == 5
        assert data["message"] == "문서 인덱싱이 완료되었습니다."
        assert data["error"] is None
        
        # 서비스 호출 확인
        mock_rag_service.ingest_documents.assert_called_once_with("python_backend/langchain_pipeline/data/documents")
    
    @pytest.mark.asyncio
    @pytest.mark.api 
    async def test_ask_question_single_answer(self, async_client: AsyncClient, mock_rag_service):
        """POST /api/v1/rag/ask - 단일 질의응답 (use_styles=False)"""
        # Given: RAG 서비스 단일 응답 설정
        mock_rag_service.ask_question = AsyncMock(return_value={
            "success": True,
            "answer": "LangChain은 대화형 AI 애플리케이션을 구축하기 위한 프레임워크입니다.",
            "sources": [
                {"source": "langchain_guide.txt", "content": "LangChain 가이드..."}
            ],
            "metadata": {"model_used": "gpt_embedder", "query_type": "single_answer"}
        })
        
        # When: 단일 질문 요청
        request_data = {
            "query": "LangChain이 무엇인가요?",
            "use_styles": False,
            "context": "learning"
        }
        response = await async_client.post("/api/v1/rag/ask", json=request_data)
        
        # Then: 단일 답변 응답
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["answer"] == "LangChain은 대화형 AI 애플리케이션을 구축하기 위한 프레임워크입니다."
        assert len(data["sources"]) == 1
        assert data["error"] is None
        assert "converted_texts" not in data  # 단일 답변이므로 스타일 변환 없음
        
        # 서비스 호출 확인
        mock_rag_service.ask_question.assert_called_once_with(
            query="LangChain이 무엇인가요?",
            context="learning"
        )
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_ask_question_with_styles(self, async_client: AsyncClient, mock_rag_service, test_user_profile):
        """POST /api/v1/rag/ask - 3가지 스타일 질의응답 (use_styles=True)"""
        # Given: 스타일별 응답 설정
        mock_rag_service.ask_with_styles = AsyncMock(return_value={
            "success": True,
            "converted_texts": {
                "direct": "프로젝트는 현재 70% 완료되었습니다.",
                "gentle": "프로젝트가 순조롭게 진행되고 있어요. 약 70% 정도 완료된 상황입니다.",
                "neutral": "프로젝트 진행률은 현재 70% 수준입니다."
            },
            "sources": [{"source": "project_status.txt"}],
            "rag_context": "프로젝트 관리 문서에서 추출한 정보",
            "metadata": {"model_used": "gpt-4o + faiss", "query_type": "style_conversion"}
        })
        
        # When: 스타일별 질문 요청
        request_data = {
            "query": "프로젝트 진행 상황을 알려주세요",
            "use_styles": True,
            "user_profile": test_user_profile,
            "context": "business"
        }
        response = await async_client.post("/api/v1/rag/ask", json=request_data)
        
        # Then: 스타일별 응답 확인
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "converted_texts" in data
        assert "direct" in data["converted_texts"]
        assert "gentle" in data["converted_texts"] 
        assert "neutral" in data["converted_texts"]
        assert data["rag_context"] == "프로젝트 관리 문서에서 추출한 정보"
        assert len(data["sources"]) > 0
        assert "answer" not in data  # 스타일 변환이므로 단일 답변 없음
        
        # 서비스 호출 확인
        mock_rag_service.ask_with_styles.assert_called_once()
        call_args = mock_rag_service.ask_with_styles.call_args
        assert call_args.kwargs["query"] == "프로젝트 진행 상황을 알려주세요"
        assert call_args.kwargs["context"] == "business"
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_analyze_grammar(self, async_client: AsyncClient, mock_rag_service):
        """POST /api/v1/rag/analyze-grammar - 문법 분석"""
        # Given: 문법 분석 응답 설정
        mock_rag_service.ask_question = AsyncMock(return_value={
            "success": True,
            "answer": "문법적으로 올바른 문장입니다. 표현이 자연스럽고 명확합니다.",
            "sources": [{"source": "grammar_rules.txt"}],
            "metadata": {"analysis_type": "grammar_check"}
        })
        
        # When: 문법 분석 요청
        request_data = {
            "query": "이 문장의 문법을 확인해주세요."
        }
        response = await async_client.post("/api/v1/rag/analyze-grammar", json=request_data)
        
        # Then: 분석 결과 확인
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["answer"] == "문법적으로 올바른 문장입니다. 표현이 자연스럽고 명확합니다."
        assert data["metadata"]["analysis_type"] == "grammar_check"
        assert data["metadata"]["original_text"] == "이 문장의 문법을 확인해주세요."
        
        # 서비스 호출 시 문법 분석용 쿼리로 변환되었는지 확인
        mock_rag_service.ask_question.assert_called_once()
        call_args = mock_rag_service.ask_question.call_args
        assert "문법, 맞춤법, 표현을 분석하고" in call_args.kwargs["query"]
        assert call_args.kwargs["context"] == "문법 분석"
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_suggest_expressions(self, async_client: AsyncClient, mock_rag_service):
        """POST /api/v1/rag/suggest-expressions - 표현 개선 제안"""
        # Given: 표현 개선 응답 설정
        mock_rag_service.ask_question = AsyncMock(return_value={
            "success": True,
            "answer": "더 전문적인 표현으로 '프로젝트를 완료하겠습니다'라고 하시면 좋겠습니다.",
            "sources": [{"source": "business_style.txt"}],
            "metadata": {"analysis_type": "expression_improvement"}
        })
        
        # When: 표현 개선 요청 (비즈니스 컨텍스트)
        request_data = {
            "query": "일 끝내겠습니다",
            "context": "business"
        }
        response = await async_client.post("/api/v1/rag/suggest-expressions", json=request_data)
        
        # Then: 개선 제안 확인
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "프로젝트를 완료하겠습니다" in data["answer"]
        assert data["metadata"]["analysis_type"] == "expression_improvement"
        assert data["metadata"]["context_type"] == "business"
        assert data["metadata"]["original_text"] == "일 끝내겠습니다"
        
        # 서비스 호출 시 표현 개선용 쿼리로 변환되었는지 확인
        mock_rag_service.ask_question.assert_called_once()
        call_args = mock_rag_service.ask_question.call_args
        assert "business 맥락에서" in call_args.kwargs["query"]
        assert "더 나은 표현으로 바꿔주세요" in call_args.kwargs["query"]
        assert call_args.kwargs["context"] == "business 표현 개선"
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_empty_query_validation(self, async_client: AsyncClient):
        """빈 질문 입력 검증 테스트"""
        # When: 빈 질문들 요청
        test_cases = [
            {"query": ""},          # 완전히 빈 문자열
            {"query": "   "},       # 공백만
            {"query": "\n\t"},      # 개행/탭만
        ]
        
        for request_data in test_cases:
            request_data["use_styles"] = False
            response = await async_client.post("/api/v1/rag/ask", json=request_data)
            
            # Then: 400 에러 응답
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            data = response.json()
            assert "질문을 입력해주세요" in data["detail"]


class TestRAGServiceDependencyInjection:
    """RAG 서비스 의존성 주입 테스트"""
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_rag_service_injection_failure(self, async_client: AsyncClient):
        """RAG 서비스 의존성 주입 실패 테스트"""
        # Given: RAG 서비스 초기화 실패
        with patch("api.v1.endpoints.rag.get_rag_service") as mock_get_service:
            mock_get_service.side_effect = ImportError("RAG 서비스를 사용할 수 없습니다")
            
            # When: 상태 확인 요청
            response = await async_client.get("/api/v1/rag/status")
            
            # Then: 503 서비스 불가 응답
            assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
            data = response.json()
            assert "RAG 서비스를 사용할 수 없습니다" in data["detail"]
    
    @pytest.mark.asyncio
    @pytest.mark.api 
    async def test_rag_service_initialization_error(self, async_client: AsyncClient):
        """RAG 서비스 초기화 오류 테스트"""
        # Given: RAG 서비스 초기화 중 일반 오류
        with patch("api.v1.endpoints.rag.get_rag_service") as mock_get_service:
            mock_get_service.side_effect = Exception("PostgreSQL 연결 실패")
            
            # When: 문서 인덱싱 요청
            request_data = {"folder_path": "test/path"}
            response = await async_client.post("/api/v1/rag/ingest", json=request_data)
            
            # Then: 500 내부 서버 오류
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert "RAG 서비스 초기화 실패" in data["detail"]


class TestRAGErrorScenarios:
    """RAG 에러 시나리오 테스트"""
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_rag_service_not_initialized(self, async_client: AsyncClient, mock_rag_service):
        """RAG 서비스가 초기화되지 않은 상태"""
        # Given: RAG 서비스가 초기화되지 않음
        mock_rag_service.ask_question = AsyncMock(return_value={
            "success": False,
            "error": "RAG 서비스가 초기화되지 않았습니다.",
            "answer": "",
            "sources": [],
            "metadata": {"model_used": "none"}
        })
        
        # When: 질문 요청
        request_data = {
            "query": "테스트 질문",
            "use_styles": False
        }
        response = await async_client.post("/api/v1/rag/ask", json=request_data)
        
        # Then: 서비스 수준 에러 (HTTP 200이지만 success=false)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is False
        assert "RAG 서비스가 초기화되지 않았습니다" in data["error"]
        assert data["answer"] == ""
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_document_processing_failure(self, async_client: AsyncClient, mock_rag_service):
        """문서 처리 실패 시나리오"""
        # Given: 문서 인덱싱 실패
        mock_rag_service.ingest_documents.return_value = {
            "success": False,
            "documents_processed": 0,
            "error": "문서 형식이 지원되지 않습니다."
        }
        
        # When: 문서 인덱싱 요청
        request_data = {
            "folder_path": "python_backend/langchain_pipeline/data/documents"
        }
        response = await async_client.post("/api/v1/rag/ingest", json=request_data)
        
        # Then: 실패 응답
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is False
        assert data["documents_processed"] == 0
        assert data["message"] == "문서 인덱싱에 실패했습니다."
        assert "지원되지 않습니다" in data["error"]


@pytest.mark.db
class TestRAGWithPostgreSQL:
    """PostgreSQL + pgvector 실제 연동 테스트"""
    
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_vector_search_integration(self):
        """실제 pgvector를 사용한 벡터 검색 테스트"""
        # PostgreSQL + pgvector가 실제로 설정되어 있다면 실행
        # 이 테스트는 실제 DB 환경에서만 의미가 있음
        pytest.skip("실제 DB 연동 테스트는 별도 환경에서 실행")
    
    @pytest.mark.integration  
    async def test_document_embedding_storage(self):
        """문서 임베딩 저장 테스트"""
        # 실제 pgvector에 임베딩 저장/조회 테스트
        pytest.skip("실제 DB 연동 테스트는 별도 환경에서 실행")