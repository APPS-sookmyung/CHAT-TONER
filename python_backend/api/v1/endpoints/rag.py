"""
RAG (Retrieval-Augmented Generation) Endpoints
문서 기반 질의응답 및 텍스트 품질 분석 엔드포인트
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional, List, Annotated
from pydantic import BaseModel
from pathlib import Path

router = APIRouter()

# Request/Response Models
class DocumentIngestRequest(BaseModel):
    folder_path: str = "python_backend/langchain_pipeline/data/documents"

class DocumentIngestResponse(BaseModel):
    success: bool
    documents_processed: int
    message: str
    error: Optional[str] = None

class RAGQueryRequest(BaseModel):
    query: str
    context: Optional[str] = None
    use_styles: bool = False
    user_profile: Optional[Dict[str, Any]] = None

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

# RAG Service 의존성 주입
def get_rag_service():
    """RAG 서비스 인스턴스 생성"""
    try:
        from services.rag_service import RAGService
        return RAGService()
    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"RAG 서비스를 사용할 수 없습니다: {str(e)}") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG 서비스 초기화 실패: {str(e)}") from e

@router.post("/rag/ingest", response_model=DocumentIngestResponse)
async def ingest_documents(
    request: DocumentIngestRequest,
    rag_service: Annotated[object, Depends(get_rag_service)]
) -> DocumentIngestResponse:
    """문서 폴더에서 RAG 벡터 DB 생성"""
    try:
        folder_path = Path(request.folder_path)
        if not folder_path.exists():
            raise HTTPException(status_code=404, detail=f"문서 폴더를 찾을 수 없습니다: {request.folder_path}")
        
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

@router.post("/rag/ask", response_model=RAGQueryResponse)
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
                user_profile=request.user_profile,
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
                context=request.context
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

@router.get("/rag/status", response_model=RAGStatusResponse)
async def get_rag_status(rag_service: Annotated[object, Depends(get_rag_service)]) -> RAGStatusResponse:
    """RAG 시스템 상태 확인"""
    try:
        status = rag_service.get_status()
        
        return RAGStatusResponse(
            rag_status=status.get("rag_status", "unknown"),
            doc_count=status.get("doc_count", 0),
            services_available=status.get("services_available", False),
            documents_path="python_backend/langchain_pipeline/data/documents",
            index_path="python_backend/langchain_pipeline/data/faiss_index"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"상태 조회 중 오류가 발생했습니다: {str(e)}")

@router.post("/rag/analyze-grammar")
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

@router.post("/rag/suggest-expressions")
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