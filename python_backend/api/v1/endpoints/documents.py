"""
Documents Endpoints (stand-alone 회사용)
파일 업로드 후 RAG 인덱싱 트리거
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List, Optional, Annotated
from pathlib import Path
import shutil

from .rag import get_rag_service  # 기존 RAG 서비스 싱글톤 재사용

router = APIRouter()


def _get_documents_path() -> Path:
    # RAG 설정의 기본 문서 폴더 사용
    from core.rag_config import get_rag_config
    cfg = get_rag_config()
    path = cfg.documents_path
    path.mkdir(parents=True, exist_ok=True)
    return path


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

