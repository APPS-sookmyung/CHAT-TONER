"""
Documents Endpoints (stand-alone 회사용)
파일 업로드 후 RAG 인덱싱 트리거
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List, Optional, Annotated, Dict
from pathlib import Path
import shutil
import os

from .rag import get_rag_service  # 기존 RAG 서비스 싱글톤 재사용
from core.container import Container

router = APIRouter()


def _get_documents_path() -> Path:
    # RAG 설정의 기본 문서 폴더 사용
    from core.rag_config import get_rag_config
    cfg = get_rag_config()
    path = cfg.documents_path
    path.mkdir(parents=True, exist_ok=True)
    return path


@router.get("/", response_model=List[str])
async def list_documents(subdir: Optional[str] = None) -> List[str]:
    """
    업로드된 문서 목록을 조회합니다.
    """
    try:
        base_dir = _get_documents_path()
        target_dir = base_dir / subdir if subdir else base_dir
        
        if not target_dir.is_dir():
            return []
            
        documents = []
        for root, _, files in os.walk(target_dir):
            for name in files:
                # base_dir를 기준으로 한 상대 경로를 반환
                relative_path = os.path.relpath(os.path.join(root, name), base_dir)
                documents.append(str(relative_path))
        
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"문서 목록 조회 실패: {e}")

@router.delete("/{document_name:path}", response_model=Dict[str, str])
async def delete_document(document_name: str) -> Dict[str, str]:
    """
    지정된 문서를 삭제합니다.
    - document_name에 하위 디렉토리 경로를 포함할 수 있습니다. (예: subdir/doc.pdf)
    """
    try:
        base_dir = _get_documents_path()
        file_path = base_dir / document_name

        if not file_path.is_file():
            raise HTTPException(status_code=404, detail=f"문서를 찾을 수 없습니다: {document_name}")

        file_path.unlink()  # 파일 삭제

        # TODO: RAG 서비스에서 해당 문서의 인덱스도 삭제하는 로직 추가 필요
        # rag_service.delete_document_from_index(str(file_path))

        return {"message": f"문서가 성공적으로 삭제되었습니다: {document_name}"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"문서 삭제 실패: {e}")


@router.post("/upload")
async def upload_documents(
    files: List[UploadFile] = File(...),
    rag_service: Annotated[object, Depends(get_rag_service)] = None,
    subdir: Optional[str] = None,
):
    """
    문서 업로드 후 기본 문서 폴더에 저장하고 인덱싱 트리거
    - 지원: pdf/txt/md/docx (그 외 확장자도 저장은 허용)
    - 단일 회사 기준: 회사 구분 없이 공용 인덱스 사용
    """
    try:
        base_dir = _get_documents_path()
        target_dir = base_dir / subdir if subdir else base_dir
        target_dir.mkdir(parents=True, exist_ok=True)

        saved = 0
        for f in files:
            dest = target_dir / f.filename
            with dest.open("wb") as out:
                shutil.copyfileobj(f.file, out)
            saved += 1

        # 업로드된 디렉토리를 인덱싱
        result = rag_service.ingest_documents(str(target_dir))
        return {
            "success": bool(result.get("success")),
            "uploaded": saved,
            "documents_processed": result.get("documents_processed", 0),
            "index_path": str(target_dir),
            "error": result.get("error") if not result.get("success") else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"업로드/인덱싱 실패: {e}")


from pydantic import BaseModel, Field

class DocumentTextIngestRequest(BaseModel):
    content: str = Field(..., description="프로토콜 텍스트 본문")
    title: Optional[str] = Field(None, description="파일명으로 사용할 제목(선택)")
    subdir: Optional[str] = Field(None, description="저장할 하위 디렉터리(선택)")


@router.post("/ingest-text")
async def ingest_text_document(
    request: DocumentTextIngestRequest,
    rag_service: Annotated[object, Depends(get_rag_service)] = None,
):
    """
    순수 텍스트로 전달된 프로토콜을 .txt 파일로 저장 후 인덱싱합니다.
    단일 회사(stand-alone) 기준 공용 인덱스에 반영됩니다.
    """
    try:
        if not request.content or not request.content.strip():
            raise HTTPException(status_code=400, detail="content 텍스트가 비어 있습니다")

        base_dir = _get_documents_path()
        target_dir = base_dir / request.subdir if request.subdir else base_dir
        target_dir.mkdir(parents=True, exist_ok=True)

        # 파일명 생성 (제목이 없으면 타임스탬프 기반)
        import re, time
        def safe_name(s: str) -> str:
            return re.sub(r"[^\w\-\.]+", "_", s).strip("._") or "protocol"

        name = safe_name(request.title) if request.title else f"protocol_{int(time.time())}"
        filepath = target_dir / f"{name}.txt"

        # 저장
        filepath.write_text(request.content, encoding="utf-8")

        # 디렉터리 인덱싱
        result = rag_service.ingest_documents(str(target_dir))
        return {
            "success": bool(result.get("success")),
            "saved_file": str(filepath),
            "documents_processed": result.get("documents_processed", 0),
            "index_path": str(target_dir),
            "error": result.get("error") if not result.get("success") else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"텍스트 인덱싱 실패: {e}")


# PDF 요약 관련 엔드포인트들
from pydantic import BaseModel
from enum import Enum

class SummaryType(str, Enum):
    BRIEF = "brief"
    DETAILED = "detailed"
    BULLET_POINTS = "bullet_points"

class PDFSummaryRequest(BaseModel):
    document_name: str = Field(..., description="요약할 PDF 파일명")
    summary_type: SummaryType = Field(SummaryType.BRIEF, description="요약 유형")

class TextSummaryRequest(BaseModel):
    text: str = Field(..., description="요약할 텍스트")
    summary_type: SummaryType = Field(SummaryType.BRIEF, description="요약 유형")


def get_pdf_summary_service():
    """PDF 요약 서비스 의존성 함수"""
    container = Container()
    return container.pdf_summary_service()


@router.post("/summarize-pdf")
async def summarize_pdf(
    request: PDFSummaryRequest,
    pdf_service: Annotated[object, Depends(get_pdf_summary_service)] = None,
):
    """
    업로드된 PDF 파일을 요약합니다.

    Args:
        request: PDF 요약 요청 (파일명, 요약 유형)
        pdf_service: PDF 요약 서비스

    Returns:
        PDF 요약 결과
    """
    try:
        base_dir = _get_documents_path()
        file_path = base_dir / request.document_name

        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"파일을 찾을 수 없습니다: {request.document_name}")

        result = await pdf_service.summarize_pdf_by_path(
            str(file_path),
            request.summary_type.value
        )

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF 요약 생성 실패: {e}")


@router.post("/summarize-text")
async def summarize_text(
    request: TextSummaryRequest,
    pdf_service: Annotated[object, Depends(get_pdf_summary_service)] = None,
):
    """
    주어진 텍스트를 요약합니다.

    Args:
        request: 텍스트 요약 요청 (텍스트, 요약 유형)
        pdf_service: PDF 요약 서비스 (텍스트 요약에도 사용)

    Returns:
        텍스트 요약 결과
    """
    try:
        result = await pdf_service.summarize_pdf_text(
            request.text,
            request.summary_type.value
        )

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"텍스트 요약 생성 실패: {e}")
