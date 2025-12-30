"""
RAG (Retrieval-Augmented Generation) Endpoints
문서 기반 질의응답 및 텍스트 품질 분석 엔드포인트
"""

import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Annotated
from services.enterprise_db_service import EnterpriseDBService
from services.profile_generator import ProfileGeneratorService
from services.document_service import DocumentService
from api.v1.schemas.conversion import UserProfile
from dependency_injector.wiring import inject, Provide
from core.container import Container

logger = logging.getLogger('chattoner.rag_endpoints') # Added logger

router = APIRouter()

# Request/Response Models
class DocumentIngestRequest(BaseModel):
    folder_path: str = "python_backend/langchain_pipeline/data/documents"
    company_id: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "folder_path": "python_backend/langchain_pipeline/data/documents",
                "company_id": "acme-co"
            }
        }

class DocumentIngestResponse(BaseModel):
    success: bool
    documents_processed: int
    message: str
    error: Optional[str] = None

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "success": True,
                    "documents_processed": 12,
                    "message": "벡터 데이터베이스 생성이 완료되었습니다. 처리된 문서 수: 12개.",
                    "error": None
                }
            ]
        }

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

from fastapi import File, UploadFile
import shutil

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Uploads a file to a temporary directory and returns the path."""
    try:
        temp_dir = Path("packages/python_backend/temp_uploads")
        temp_dir.mkdir(exist_ok=True)
        file_path = temp_dir / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"filePath": str(file_path)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {e}")

@router.post(
    "/ingest",
    response_model=DocumentIngestResponse,
    status_code=200,
    responses={
        200: {
            "description": "항상 200 OK로 응답합니다. success=false인 경우에도 오류를 message/error에 담아 반환합니다.",
            "content": {
                "application/json": {
                    "examples": {
                        "success": {
                            "summary": "성공",
                            "value": {
                                "success": True,
                                "documents_processed": 5,
                                "message": "벡터 데이터베이스 생성이 완료되었습니다. 처리된 문서 수: 5개.",
                                "error": None
                            }
                        },
                        "folder_missing": {
                            "summary": "경로 없음",
                            "value": {
                                "success": False,
                                "documents_processed": 0,
                                "message": "요청하신 문서로 벡터 DB 생성을 준비했어요. 다만 지정하신 경로가 보이지 않아 진행을 보류했어요. 경로를 확인해 주시면 바로 처리할게요.",
                                "error": "not_found: ./missing/path"
                            }
                        },
                        "internal_error": {
                            "summary": "내부 오류",
                            "value": {
                                "success": False,
                                "documents_processed": 0,
                                "message": "벡터 DB 생성 요청을 접수했어요. 잠시 후 다시 시도할게요.",
                                "error": "RuntimeError: ..."
                            }
                        }
                    }
                }
            }
        }
    }
)
@inject
async def ingest_documents(
    request: DocumentIngestRequest,
    rag_service: Annotated[object, Depends(get_rag_service)],
    db_service: EnterpriseDBService = Depends(Provide[Container.enterprise_db_service]),
    profile_generator: ProfileGeneratorService = Depends(Provide[Container.profile_generator_service]),
    document_service: DocumentService = Depends(Provide[Container.document_service]),
) -> DocumentIngestResponse:
    """문서 폴더에서 RAG 벡터 DB 생성 (항상 200 OK 폴백)"""
    try:
        from pathlib import Path

        current_dir = Path.cwd()
        folder_path = current_dir / request.folder_path

        logger.info(f"RAG Ingest: Current dir: {current_dir}")
        logger.info(f"RAG Ingest: Requested path: {request.folder_path}")
        logger.info(f"RAG Ingest: Final folder_path: {folder_path}")

        async def craft_ingest_message(success: bool, processed: int, note: str | None = None) -> str:
            """LLM을 사용해 자연스러운 한국어 상태 메시지 생성.

            - success: 처리 성공 여부
            - processed: 처리된 문서 개수
            - note: 추가 설명(에러/경로 안내 등)
            """
            try:
                openai_service = getattr(rag_service, "openai_service", None)
                # 성공 시에는 고정 문구로 완료 메시지를 보장
                if success:
                    return f"벡터 데이터베이스 생성이 완료되었습니다. 처리된 문서 수: {processed}개."

                # 실패/보류 시 기본 안내 문구
                base_statement = f"벡터 데이터베이스 생성이 보류/실패되었어요. 처리된 문서 수: {processed}개."
                if not openai_service:
                    return base_statement if not note else f"{base_statement} 참고: {note}"

                # Mock 모드에서는 간결한 고정 문구로 반환
                if getattr(openai_service, "mock_mode", False):
                    return base_statement if not note else f"{base_statement} 참고: {note}"

                system = (
                    "당신은 한국어 제품 어시스턴트입니다. 사용자가 이해하기 쉬운 한두 문장으로, "
                    "긍정적이면서도 정확하게 현재 작업 상태를 안내하세요. 불필요한 사족은 피하고, 숫자 정보(개수 등)는 그대로 유지하세요."
                )
                status = "보류 또는 실패"
                user_prompt = (
                    f"상황: RAG 문서 주입 결과.\n"
                    f"상태: {status}\n"
                    f"처리된 문서 개수: {processed}개\n"
                    f"비고: {note or '없음'}\n\n"
                    f"위 내용을 바탕으로 사용자에게 보여줄 친절하고 간결한 한국어 상태 메시지를 1~2문장으로 작성해 주세요."
                )
                # LLM 호출
                text = await openai_service.generate_text(user_prompt, system=system, temperature=0.3, max_tokens=120)
                return text.strip() or (base_statement if not note else f"{base_statement} 참고: {note}")
            except Exception as _e:
                # LLM 실패 시 기본 안내로 폴백
                return base_statement if not note else f"{base_statement} 참고: {note}"

        if not folder_path.exists():
            # 폴더가 없더라도 200 OK로 폴백 응답 (LLM 가공 메시지)
            friendly = await craft_ingest_message(
                success=False,
                processed=0,
                note=f"지정 경로를 찾을 수 없음: {folder_path}"
            )
            return DocumentIngestResponse(
                success=False,
                documents_processed=0,
                message=friendly,
                error=f"not_found: {folder_path}"
            )

        if request.company_id:
            result = rag_service.ingest_company_documents(request.company_id, str(folder_path))
            if result.get("success"):
                try:
                    # Get document contents
                    documents = document_service.get_documents_from_folder(str(folder_path))
                    
                    # Generate profile from documents
                    generated_profile = await profile_generator.create_profile_from_documents(request.company_id, documents)

                    # Get existing profile
                    existing_profile = await db_service.get_company_profile(request.company_id)
                    if existing_profile:
                        # Update profile
                        existing_profile["generated_profile"] = f"{existing_profile.get('generated_profile', '')}\n\n[자동 생성된 온보딩 특성]\n{generated_profile}"
                        
                        # Upsert profile
                        await db_service.upsert_company_profile(
                            company_id=existing_profile["company_id"],
                            company_name=existing_profile["company_name"],
                            industry=existing_profile["industry"],
                            team_size=existing_profile["team_size"],
                            primary_business=existing_profile["primary_business"],
                            communication_style=existing_profile["communication_style"],
                            main_channels=existing_profile["main_channels"],
                            target_audience=existing_profile["target_audience"],
                            generated_profile=existing_profile["generated_profile"],
                            survey_data=existing_profile["survey_data"],
                        )
                        logger.info(f"문서 기반 프로필 업데이트 완료: {request.company_id}")
                except Exception as e:
                    logger.error(f"문서 기반 프로필 업데이트 실패: {e}")
        else:
            result = rag_service.ingest_documents(str(folder_path))

        ok = result.get("success", False)
        count = result.get("documents_processed", 0)
        note = result.get("error") if not ok else None
        friendly = await craft_ingest_message(success=ok, processed=count, note=note)

        return DocumentIngestResponse(
            success=ok,
            documents_processed=count,
            message=friendly,
            error=result.get("error") if not ok else None
        )

    except Exception as e:
        # 모든 예외도 200 OK로 폴백하여 상위 호출자 실패 방지 (LLM 가공 메시지)
        logger.error(f"문서 인덱싱 폴백 오류: {e}")
        try:
            # 가능하면 LLM으로 안내 메시지 생성
            openai_service = getattr(rag_service, "openai_service", None)
            if openai_service and not getattr(openai_service, "mock_mode", False):
                system = (
                    "당신은 한국어 제품 어시스턴트입니다. 기술적 문제로 처리가 보류된 상황에서, "
                    "사용자가 이해하기 쉬운 한두 문장으로 재시도 안내와 다음 행동을 친절하게 제시하세요."
                )
                user_prompt = (
                    f"상황: RAG 문서 주입 예외 발생.\n"
                    f"오류: {str(e)[:200]}\n\n"
                    f"간결한 한국어 안내문 1~2문장으로 작성"
                )
                msg = await openai_service.generate_text(user_prompt, system=system, temperature=0.3, max_tokens=120)
            else:
                msg = "벡터 DB 생성 요청을 접수했어요. 잠시 후 다시 시도할게요."
        except Exception:
            msg = "벡터 DB 생성 요청을 접수했어요. 잠시 후 다시 시도할게요."

        return DocumentIngestResponse(
            success=False,
            documents_processed=0,
            message=msg,
            error=str(e)
        )

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

class JustifyScoreResponse(BaseModel):
    justifications: List[str]

@router.get("/justify-score", response_model=JustifyScoreResponse)
async def justify_score(
    score_type: str,
    company_id: Optional[str] = None,
    rag_service: Annotated[object, Depends(get_rag_service)] = None
) -> JustifyScoreResponse:
    """점수 산정 근거를 RAG를 통해 조회"""
    
    query_map = {
        "formality": "글의 격식에 대한 기준",
        "readability": "글의 가독성을 높이는 방법",
        "grammar": "자주 틀리는 문법 및 맞춤법",
        "protocol": "회사의 커뮤니케이션 프로토콜"
    }
    
    query = query_map.get(score_type)
    if not query:
        raise HTTPException(status_code=400, detail=f"Invalid score_type: {score_type}")
        
    try:
        result = await rag_service.ask_question(
            query=query,
            context=f"{score_type} 점수 근거 조회",
            company_id=company_id
        )
        
        if not result.get("success"):
            return JustifyScoreResponse(justifications=[])
            
        sources = result.get("sources", [])
        justifications = [source.get("page_content", "") for source in sources[:3]]
        
        return JustifyScoreResponse(justifications=justifications)
        
    except Exception as e:
        logger.error(f"점수 근거 조회 중 오류: {e}")
        raise HTTPException(status_code=500, detail="점수 근거를 조회하는 중 오류가 발생했습니다.")
