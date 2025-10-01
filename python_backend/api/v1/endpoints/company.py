"""
Company Endpoints
기업별 데이터(문서 등) 관리를 위한 API 엔드포인트
"""
import logging
import shutil
import tempfile
from pathlib import Path
from typing import Annotated, Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel

from api.v1.dependencies import get_document_service  # 문서 서비스 의존성
from services.document_service import DocumentService

logger = logging.getLogger('chattoner')
router = APIRouter()


class DocumentUploadResponse(BaseModel):
    success: bool
    company_id: str
    document_id: str
    chunks_processed: int
    message: str
    error: Optional[str] = None

@router.post(
    "/documents/upload", 
    response_model=DocumentUploadResponse,
    responses={
        400: {"description": "잘못된 요청 (예: 파일 이름 없음, PDF 아닌 파일)"},
        500: {"description": "서버 내부 오류 (파일 처리 또는 임베딩 실패)"},
    },
)
async def upload_company_document(
    company_id: Annotated[str, Form()],
    document_id: Annotated[str, Form()],
    file: Annotated[UploadFile, File()],
    doc_service: Annotated[DocumentService, Depends(get_document_service)]
) -> DocumentUploadResponse:
    """
    특정 기업의 문서를 업로드하고 임베딩합니다.

    - **company_id**: 문서를 소유한 기업의 고유 ID
    - **document_id**: 업로드하는 문서의 고유 ID
    - **file**: 업로드할 문서 파일 (PDF)
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="파일 이름이 없습니다.")

    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="PDF 파일만 업로드할 수 있습니다.")

    # 파일을 안전하게 처리하기 위해 임시 디렉터리 사용
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file_path = Path(temp_dir) / file.filename
        try:
            # 1. 업로드된 파일을 임시 위치에 저장
            with open(temp_file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            logger.info(f"임시 파일 저장 완료: {temp_file_path}")

            # 2. DocumentService를 사용하여 문서 처리 및 임베딩
            result = await doc_service.process_and_embed_document(
                file_path=temp_file_path,
                company_id=company_id,
                document_id=document_id
            )

            # 3. 결과에 따라 응답 반환
            if not result.get("success"):
                error_message = result.get("error", "알 수 없는 오류")
                logger.error(f"문서 처리 실패: {error_message}")
                raise HTTPException(status_code=500, detail=f"문서 처리 실패: {error_message}")
            
            logger.info(f"문서 업로드 및 임베딩 성공: company_id={company_id}, document_id={document_id}")
            return DocumentUploadResponse(
                success=True,
                company_id=result["company_id"],
                document_id=result["document_id"],
                chunks_processed=result["chunks_processed"],
                message="문서가 성공적으로 처리 및 임베딩되었습니다."
            )

        except HTTPException:
            raise # FastAPI의 HTTPException은 그대로 전달
        except Exception as e:
            logger.error(f"문서 업로드 처리 중 예외 발생: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"서버 내부 오류: {e}")
        finally:
            # file.file 객체는 FastAPI가 관리하므로 여기서 닫지 않습니다.
            pass
