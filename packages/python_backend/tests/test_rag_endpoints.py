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
        # 메시지는 벡터 DB 생성 완료 문구를 포함하도록 변경됨
        assert "벡터 데이터베이스 생성이 완료되었습니다" in data["message"]
        assert data["error"] is None
        
        # 서비스 호출 확인
        mock_rag_service.ingest_documents.assert_called_once_with("python_backend/langchain_pipeline/data/documents")
    
    @pytest.mark.asyncio
    @pytest.mark.api 
    async def test_ask_question_single_answer_long_text(self, async_client: AsyncClient, mock_rag_service):
        """POST /api/v1/rag/ask - 긴 텍스트 단일 질의응답 (use_styles=False)"""
        # Given: 긴 텍스트 응답 설정
        long_answer = """
        LangChain은 대규모 언어 모델(LLM)을 활용한 애플리케이션 개발을 위한 종합적인 프레임워크입니다. 
        이 프레임워크는 개발자들이 복잡한 AI 시스템을 보다 쉽게 구축할 수 있도록 설계되었으며, 
        특히 문서 검색, 질의응답, 텍스트 생성, 대화형 AI 등의 기능을 제공합니다.
        
        LangChain의 핵심 구성 요소는 다음과 같습니다:
        1. Chains: 여러 컴포넌트를 연결하여 복잡한 워크플로우를 구성
        2. Agents: 자율적으로 도구를 사용하고 결정을 내리는 AI 에이전트
        3. Memory: 대화 히스토리나 컨텍스트를 관리하는 메모리 시스템
        4. Document Loaders: 다양한 형태의 문서를 로드하고 처리
        5. Vector Stores: 임베딩 벡터를 저장하고 검색하는 시스템
        6. Retrievers: 관련 문서나 정보를 검색하는 컴포넌트
        
        특히 RAG(Retrieval-Augmented Generation) 시스템 구축에 있어서 LangChain은 매우 강력한 도구입니다. 
        문서를 청크 단위로 분할하고, 각 청크를 벡터로 임베딩한 후, 유사도 검색을 통해 관련 정보를 찾아 
        최종적으로 LLM에게 컨텍스트로 제공하는 전체 파이프라인을 효율적으로 구현할 수 있습니다.
        
        또한 LangChain은 다양한 LLM 제공업체(OpenAI, Anthropic, Cohere 등)와의 통합을 지원하며,
        로컬 모델과 클라우드 모델 모두를 활용할 수 있는 유연성을 제공합니다. 이를 통해 개발자는
        비용 효율성과 성능을 고려하여 최적의 모델 조합을 선택할 수 있습니다.
        """
        
        mock_rag_service.ask_question = AsyncMock(return_value={
            "success": True,
            "answer": long_answer.strip(),
            "sources": [
                {
                    "source": "langchain_comprehensive_guide.txt",
                    "content": "LangChain 프레임워크의 전체적인 아키텍처와 구성 요소들에 대한 상세한 설명을 포함한 가이드 문서입니다. 이 문서는 초보자부터 고급 사용자까지 모든 레벨의 개발자들이 LangChain을 효과적으로 활용할 수 있도록 단계별로 설명되어 있습니다.",
                    "chunk_id": "section_1_intro",
                    "similarity_score": 0.95
                },
                {
                    "source": "rag_implementation_patterns.txt", 
                    "content": "RAG 시스템 구현을 위한 다양한 패턴과 베스트 프랙티스를 다루는 문서입니다. 문서 처리, 벡터 스토어 선택, 검색 최적화, 프롬프트 엔지니어링 등의 실무적인 내용들을 포함하고 있으며, 실제 프로덕션 환경에서의 적용 사례들도 함께 제공됩니다.",
                    "chunk_id": "pattern_rag_basic",
                    "similarity_score": 0.89
                }
            ],
            "metadata": {
                "model_used": "gpt_embedder", 
                "query_type": "single_answer",
                "processing_time": "2.3s",
                "token_count": 456,
                "context_length": 1280
            }
        })
        
        # When: 복잡한 긴 질문 요청
        long_query = """
        LangChain 프레임워크에 대해 자세히 설명해주세요. 
        특히 RAG 시스템 구축 시 LangChain의 주요 구성 요소들이 어떻게 활용되는지,
        그리고 다른 LLM 프레임워크들과 비교했을 때의 장점은 무엇인지 포함해서
        실무에서 사용할 때 고려해야 할 점들까지 종합적으로 알려주세요.
        """
        
        request_data = {
            "query": long_query.strip(),
            "use_styles": False,
            "context": "technical_documentation"
        }
        response = await async_client.post("/api/v1/rag/ask", json=request_data)
        
        # Then: 상세한 긴 답변 응답 확인
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert len(data["answer"]) > 500  # 긴 답변 확인
        assert "LangChain" in data["answer"]
        assert "RAG" in data["answer"]
        assert "구성 요소" in data["answer"]
        assert len(data["sources"]) == 2  # 복수 소스 확인
        assert data["sources"][0]["similarity_score"] == 0.95
        assert data["error"] is None
        assert "converted_texts" not in data  # 단일 답변이므로 스타일 변환 없음
        
        # 메타데이터 확인
        assert data["metadata"]["token_count"] == 456
        assert data["metadata"]["context_length"] == 1280
        
        # 서비스 호출 확인
        mock_rag_service.ask_question.assert_called_once_with(
            query=long_query.strip(),
            context="technical_documentation"
        )
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_ask_question_with_styles_long_text(self, async_client: AsyncClient, mock_rag_service, test_user_profile):
        """POST /api/v1/rag/ask - 긴 텍스트 3가지 스타일 질의응답 (use_styles=True)"""
        # Given: 긴 텍스트 스타일별 응답 설정
        mock_rag_service.ask_with_styles = AsyncMock(return_value={
            "success": True,
            "converted_texts": {
                "direct": """
                프로젝트는 현재 70% 완료 상태입니다. 주요 진행 사항은 다음과 같습니다:
                
                Completed tasks:
                - 요구사항 분석 및 설계 단계 (100%)
                - 백엔드 API 개발 (90%)
                - 데이터베이스 스키마 구축 (100%)
                - 사용자 인증 시스템 (95%)
                
                In-progress tasks:
                - 프론트엔드 UI/UX 개발 (60%)
                - 테스트 케이스 작성 (40%)
                - 성능 최적화 (30%)
                
                ⏳ 예정된 작업:
                - 통합 테스트 및 QA
                - 배포 환경 설정
                - 사용자 가이드 작성
                
                현재 일정대로 진행되고 있으며, 다음 주까지 80% 완료 예정입니다.
                """,
                "gentle": """
                안녕하세요! 프로젝트 진행 상황에 대해 말씀드리겠습니다.
                
                현재 전체적으로 약 70% 정도 완료된 상황이에요. 순조롭게 진행되고 있어서 다행입니다.
                
                Well-finished parts:
                - 요구사항 분석과 설계는 이미 완전히 끝났어요
                - 백엔드 API 작업도 거의 다 완료되어 가고 있습니다 (90%)
                - 데이터베이스 설정은 모두 마쳤습니다
                - 로그인/회원가입 기능도 거의 다 완성되었어요
                
                Currently working parts:
                - 사용자가 보는 화면 작업을 계속 진행하고 있어요 (60%)
                - 테스트 코드도 차근차근 작성하고 있습니다 (40%)
                - 시스템이 더 빠르게 동작하도록 개선 작업도 병행하고 있어요
                
                앞으로 남은 작업들도 계획대로 차근차근 진행할 예정이니 걱정하지 마세요.
                다음 주쯤이면 80% 정도까지는 완료될 것 같습니다!
                """,
                "neutral": """
                프로젝트 전체 진행률은 현재 70% 수준으로 파악됩니다.
                
                【완료된 항목】
                • 요구사항 분석 및 시스템 설계: 100% 완료
                • 백엔드 API 서버 개발: 90% 완료
                • 데이터베이스 스키마 및 초기 설정: 100% 완료  
                • 사용자 인증 및 권한 관리 모듈: 95% 완료
                
                【진행 중인 항목】
                • 프론트엔드 사용자 인터페이스 개발: 60% 진행
                • 단위 테스트 및 통합 테스트 케이스 작성: 40% 진행
                • 시스템 성능 최적화 작업: 30% 진행
                
                【향후 계획】
                • 전체 시스템 통합 테스트 수행
                • 프로덕션 환경 배포 설정
                • 최종 사용자 문서화 작업
                
                일정 준수율은 양호한 편이며, 예상 완료 시점은 다음 주 말경으로 전망됩니다.
                (전체 진행률 80% 달성 목표)
                """
            },
            "sources": [
                {
                    "source": "project_status_weekly_report.txt",
                    "content": "프로젝트 주간 보고서입니다. 각 팀별 진행 상황, 완료된 마일스톤, 현재 진행 중인 작업, 이슈 사항 및 리스크 요소들을 종합적으로 정리한 문서입니다. 매주 목요일마다 업데이트되며, 프로젝트 매니저와 이해관계자들이 현재 상황을 파악할 수 있도록 상세한 메트릭과 함께 제공됩니다.",
                    "chunk_id": "week_12_summary",
                    "similarity_score": 0.94
                },
                {
                    "source": "development_milestone_tracker.txt",
                    "content": "개발 마일스톤 추적 문서로, 각 개발 단계별 목표와 실제 달성 현황을 비교 분석한 자료입니다. 기능별 개발 진도, 코드 리뷰 상태, 테스트 커버리지, 성능 지표 등을 포함하며, 개발팀의 생산성과 품질 관리 현황을 종합적으로 모니터링하는 데 사용됩니다.",
                    "chunk_id": "milestone_phase_3",
                    "similarity_score": 0.88
                }
            ],
            "rag_context": "프로젝트 관리 문서 및 개발 진행 상황 보고서에서 추출된 최신 정보로, 각 개발 단계별 완료율과 향후 계획을 포함한 종합적인 프로젝트 현황 데이터",
            "metadata": {
                "model_used": "gpt-4o + faiss", 
                "query_type": "style_conversion",
                "processing_time": "4.7s",
                "total_tokens": 1250,
                "style_variants": 3,
                "context_chunks": 5
            }
        })
        
        # When: 복잡한 긴 프로젝트 상황 질문 (스타일별)
        long_business_query = """
        현재 진행 중인 프로젝트의 전체적인 상황을 상세히 파악하고 싶습니다.
        각 개발 단계별 진행률과 완료된 작업들, 그리고 아직 남은 작업들의 목록,
        예상 완료 시점과 함께 현재까지의 성과와 향후 계획을 포함해서
        종합적인 프로젝트 현황 보고를 부탁드립니다.
        """
        
        request_data = {
            "query": long_business_query.strip(),
            "use_styles": True,
            "user_profile": test_user_profile,
            "context": "business_report"
        }
        response = await async_client.post("/api/v1/rag/ask", json=request_data)
        
        # Then: 긴 텍스트 스타일별 응답 확인
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "converted_texts" in data
        
        # 각 스타일별 응답 길이 및 내용 확인
        assert len(data["converted_texts"]["direct"]) > 300
        assert len(data["converted_texts"]["gentle"]) > 400
        assert len(data["converted_texts"]["neutral"]) > 350
        
        # 직접적 스타일 특성 확인
        direct_text = data["converted_texts"]["direct"]
        assert "70% 완료" in direct_text
        assert "Completed tasks" in direct_text or "완료된 작업" in direct_text
        
        # 부드러운 스타일 특성 확인  
        gentle_text = data["converted_texts"]["gentle"]
        assert "안녕하세요" in gentle_text or "말씀드리겠습니다" in gentle_text
        assert "Well-finished" in gentle_text or "다행입니다" in gentle_text
        
        # 중립적 스타일 특성 확인
        neutral_text = data["converted_texts"]["neutral"]
        assert "파악됩니다" in neutral_text or "전망됩니다" in neutral_text
        assert "【" in neutral_text or "•" in neutral_text
        
        # RAG 컨텍스트 및 소스 확인
        assert len(data["rag_context"]) > 100
        assert "프로젝트 관리 문서" in data["rag_context"]
        assert len(data["sources"]) == 2
        assert data["sources"][0]["similarity_score"] > 0.85
        
        # 메타데이터 확인
        assert data["metadata"]["style_variants"] == 3
        assert data["metadata"]["total_tokens"] == 1250
        assert "answer" not in data  # 스타일 변환이므로 단일 답변 없음
        
        # 서비스 호출 확인
        mock_rag_service.ask_with_styles.assert_called_once()
        call_args = mock_rag_service.ask_with_styles.call_args
        assert call_args.kwargs["query"] == long_business_query.strip()
        assert call_args.kwargs["context"] == "business_report"
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_analyze_grammar_long_text(self, async_client: AsyncClient, mock_rag_service):
        """POST /api/v1/rag/analyze-grammar - 긴 텍스트 문법 분석"""
        # Given: 긴 텍스트 문법 분석 응답 설정
        long_grammar_analysis = """
        전체적으로 문법적인 구조는 올바르게 작성되었습니다. 다만 몇 가지 개선할 수 있는 부분들이 있습니다:

        **Grammar and spelling analysis results:**

        **Correct parts:**
        - 문장의 기본 구조(주어-목적어-서술어)가 적절히 배치되어 있습니다
        - 조사 사용이 대부분 정확합니다
        - 문장 간 연결이 자연스럽게 이어지고 있습니다
        - 전문 용어 사용이 맥락에 적합합니다

        **Improvement suggestions:**
        1. "~에 대해서"를 "~에 대해"로 간소화하면 더 자연스럽습니다
        2. 일부 긴 문장들을 두 개로 나누면 가독성이 향상됩니다
        3. 반복되는 어미 "~습니다"를 다양하게 변화시키면 좋겠습니다
        4. 몇 개의 외래어 표기에서 띄어쓰기 확인이 필요합니다

        **Style consistency evaluation:**
        - 전체적으로 격식체로 통일되어 있어 좋습니다
        - 비즈니스 문서에 적합한 톤을 유지하고 있습니다
        - 전문성과 정중함의 균형이 잘 맞춰져 있습니다
        """
        
        mock_rag_service.ask_question = AsyncMock(return_value={
            "success": True,
            "answer": long_grammar_analysis.strip(),
            "sources": [
                {
                    "source": "korean_grammar_comprehensive_guide.txt",
                    "content": "한국어 문법의 종합적인 가이드로, 올바른 문장 구조, 조사 사용법, 어미 변화, 띄어쓰기 규칙 등을 상세히 다루고 있습니다. 특히 비즈니스 문서와 공식 문서 작성 시 주의해야 할 문법적 요소들과 표준 맞춤법 규정에 대한 실무적인 내용들을 포함하고 있어, 전문적인 글쓰기에 도움이 됩니다.",
                    "chunk_id": "formal_writing_grammar",
                    "similarity_score": 0.92
                }
            ],
            "metadata": {
                "analysis_type": "grammar_check",
                "text_length": 425,
                "grammar_score": 8.5,
                "improvement_points": 4
            }
        })
        
        # When: 긴 텍스트 문법 분석 요청
        long_text_to_analyze = """
        현재 저희 회사에서는 새로운 디지털 전환 프로젝트에 대해서 검토를 진행하고 있습니다.
        이 프로젝트는 기존의 레거시 시스템들을 모던한 클라우드 기반 아키텍처로 이전하는 것을 목표로 하고 있으며,
        동시에 사용자 경험의 개선과 업무 효율성의 증대를 추구하고 있습니다.
        전체적인 프로젝트 범위는 다음과 같습니다. 첫번째로 기존 데이터베이스의 마이그레이션 작업이 있습니다.
        두번째로는 새로운 API 시스템의 구축 작업이 필요합니다.
        """
        
        request_data = {
            "query": long_text_to_analyze.strip()
        }
        response = await async_client.post("/api/v1/rag/analyze-grammar", json=request_data)
        
        # Then: 상세한 문법 분석 결과 확인
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert len(data["answer"]) > 400  # 긴 분석 결과 확인
        assert "문법" in data["answer"]
        assert "개선" in data["answer"]
        assert "Correct parts" in data["answer"] or "올바른 부분" in data["answer"]
        assert "제안" in data["answer"]
        assert data["metadata"]["analysis_type"] == "grammar_check"
        assert data["metadata"]["original_text"] == long_text_to_analyze.strip()
        assert data["metadata"]["text_length"] == 425
        assert data["metadata"]["grammar_score"] == 8.5
        
        # 서비스 호출 확인
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
