"""
RAG (Retrieval-Augmented Generation) Endpoints
문서 기반 질의응답 및 텍스트 품질 분석 엔드포인트
"""

import logging # Added import
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional, List, Annotated
from pydantic import BaseModel
from api.v1.schemas.conversion import UserProfile
from pathlib import Path
from core.config import get_settings # Added import

logger = logging.getLogger('chattoner.rag_endpoints') # Added logger

router = APIRouter()

# Request/Response Models
class DocumentIngestRequest(BaseModel):
    folder_path: str = "python_backend/langchain_pipeline/data/documents"
    company_id: Optional[str] = None

class DocumentIngestResponse(BaseModel):
    success: bool
    documents_processed: int
    message: str
    error: Optional[str] = None

class RAGQueryRequest(BaseModel):
    query: str
    context: Optional[str] = None
    use_styles: bool = False
    user_profile: Optional[UserProfile] = None
    company_id: Optional[str] = None

class RAGQueryResponse(BaseModel):
    success: bool
    answer: Optional[str] = None
    converted_texts: Optional[Dict[str, str]] = None
    sources: List[Dict[str, Any]] = []
    rag_context: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = {}

class RAGStatusResponse(BaseModel):
    rag_status: str
    doc_count: int
    services_available: bool
    documents_path: str
    index_path: str

def get_rag_service():
    """컨테이너에서 RAG 서비스 싱글톤 인스턴스 반환 (성능 최적화)"""
    from core.container import Container
    container = Container()
    return container.rag_service()

@router.post("/ingest", response_model=DocumentIngestResponse)
async def ingest_documents(
    request: DocumentIngestRequest,
    rag_service: Annotated[object, Depends(get_rag_service)]
) -> DocumentIngestResponse:
    """문서 폴더에서 RAG 벡터 DB 생성"""
    try:
        # 로컬 개발 환경에서는 현재 작업 디렉토리 기준으로 상대 경로 사용
        import os
        from pathlib import Path

        # 현재 작업 디렉토리에서 상대 경로로 문서 폴더 찾기
        current_dir = Path.cwd()
        folder_path = current_dir / request.folder_path

        print(f"RAG Ingest: Current dir: {current_dir}")
        print(f"RAG Ingest: Requested path: {request.folder_path}")
        print(f"RAG Ingest: Final folder_path: {folder_path}")

        if not folder_path.exists():
            raise HTTPException(status_code=404, detail=f"문서 폴더를 찾을 수 없습니다: {folder_path}")
        
        if request.company_id:
            result = rag_service.ingest_company_documents(request.company_id, str(folder_path))
        else:
            result = rag_service.ingest_documents(str(folder_path))
        
        return DocumentIngestResponse(
            success=result.get("success", False),
            documents_processed=result.get("documents_processed", 0),
            message="문서 인덱싱이 완료되었습니다." if result.get("success") else "문서 인덱싱에 실패했습니다.",
            error=result.get("error") if not result.get("success") else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"문서 인덱싱 중 오류가 발생했습니다: {str(e)}")

@router.post("/ask", response_model=RAGQueryResponse)
async def ask_rag_question(
    request: RAGQueryRequest,
    rag_service: Annotated[object, Depends(get_rag_service)]
) -> RAGQueryResponse:
    """RAG 기반 질의응답"""
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="질문을 입력해주세요.")
        
        if request.use_styles and request.user_profile:
            # 3가지 스타일 변환
            result = await rag_service.ask_with_styles(
                query=request.query,
                user_profile=(request.user_profile.model_dump() if request.user_profile else None),
                context=request.context or "personal"
            )
            
            return RAGQueryResponse(
                success=result.get("success", False),
                converted_texts=result.get("converted_texts", {}),
                sources=result.get("sources", []),
                rag_context=result.get("rag_context"),
                error=result.get("error") if not result.get("success") else None,
                metadata=result.get("metadata", {})
            )
        else:
            # 단일 답변
            result = await rag_service.ask_question(
                query=request.query,
                context=request.context,
                company_id=request.company_id
            )
            
            return RAGQueryResponse(
                success=result.get("success", False),
                answer=result.get("answer"),
                sources=result.get("sources", []),
                error=result.get("error") if not result.get("success") else None,
                metadata=result.get("metadata", {})
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"질의응답 중 오류가 발생했습니다: {str(e)}")

@router.get("/status", response_model=RAGStatusResponse)
async def get_rag_status(rag_service: Annotated[object, Depends(get_rag_service)]) -> RAGStatusResponse:
    """RAG 시스템 상태 확인"""
    try:
        status = rag_service.get_status()
        
        from core.rag_config import get_rag_config
        cfg = get_rag_config()
        return RAGStatusResponse(
            rag_status=status.get("rag_status", "unknown"),
            doc_count=status.get("doc_count", 0),
            services_available=status.get("services_available", False),
            documents_path=str(cfg.documents_path),
            index_path=str(cfg.faiss_index_path)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"상태 조회 중 오류가 발생했습니다: {str(e)}")

@router.post("/analyze-grammar")
async def analyze_text_grammar(
    request: RAGQueryRequest,
    rag_service: Annotated[object, Depends(get_rag_service)]
) -> RAGQueryResponse:
    """RAG 기반 문법 분석 (GPT 대신 문서 기반)"""
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="분석할 텍스트를 입력해주세요.")
        
        # 문법 분석을 위한 특별한 쿼리 구성
        grammar_query = f"다음 텍스트의 문법, 맞춤법, 표현을 분석하고 개선사항을 제시해주세요: {request.query}"
        
        result = await rag_service.ask_question(
            query=grammar_query,
            context="문법 분석"
        )
        
        return RAGQueryResponse(
            success=result.get("success", False),
            answer=result.get("answer"),
            sources=result.get("sources", []),
            error=result.get("error") if not result.get("success") else None,
            metadata={
                **result.get("metadata", {}),
                "analysis_type": "grammar_check",
                "original_text": request.query
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"문법 분석 중 오류가 발생했습니다: {str(e)}")

@router.post("/suggest-expressions")
async def suggest_better_expressions(
    request: RAGQueryRequest,
    rag_service: Annotated[object, Depends(get_rag_service)]
) -> RAGQueryResponse:
    """RAG 기반 표현 개선 제안"""
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="개선할 텍스트를 입력해주세요.")
        
        # 표현 개선을 위한 특별한 쿼리 구성
        context_type = request.context or "business"
        improvement_query = f"{context_type} 맥락에서 다음 텍스트를 더 나은 표현으로 바꿔주세요: {request.query}"
        
        result = await rag_service.ask_question(
            query=improvement_query,
            context=f"{context_type} 표현 개선"
        )
        
        return RAGQueryResponse(
            success=result.get("success", False),
            answer=result.get("answer"),
            sources=result.get("sources", []),
            error=result.get("error") if not result.get("success") else None,
            metadata={
                **result.get("metadata", {}),
                "analysis_type": "expression_improvement",
                "context_type": context_type,
                "original_text": request.query
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"표현 개선 제안 중 오류가 발생했습니다: {str(e)}")
