from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
import io

from services.embedding_service import EmbeddingService
from services.vector_store_pg import VectorStorePG


router = APIRouter(tags=["kb"])


class UploadResponse(BaseModel):
    tenant_id: str
    doc_id: str
    chunks: int


def _extract_text(filename: str, data: bytes) -> str:
    name = (filename or "").lower()
    if name.endswith(".txt"):
        try:
            return data.decode("utf-8", errors="ignore")
        except Exception:
            return data.decode("latin-1", errors="ignore")
    if name.endswith(".pdf"):
        try:
            import pdfplumber  # type: ignore

            text_parts: List[str] = []
            with pdfplumber.open(io.BytesIO(data)) as pdf:
                for page in pdf.pages:
                    text_parts.append(page.extract_text() or "")
            return "\n".join(text_parts)
        except Exception as e:
            raise HTTPException(501, f"PDF parsing not available: {e}")
    raise HTTPException(400, "Unsupported file type. Use .pdf or .txt")


def _chunk(text: str, target: int = 800) -> List[str]:
    out: List[str] = []
    buf = []
    count = 0
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if count + len(line) > target and buf:
            out.append(" ".join(buf))
            buf, count = [], 0
        buf.append(line)
        count += len(line)
    if buf:
        out.append(" ".join(buf))
    return out or ([text] if text else [])


@router.post("/upload", response_model=UploadResponse)
async def upload(
    tenant_id: str = Form(...),
    category: str = Form("protocol"),
    doc_id: Optional[str] = Form(None),
    file: UploadFile = File(...),
):
    raw = await file.read()
    text = _extract_text(file.filename, raw)
    chunks = _chunk(text)
    embedder = EmbeddingService(provider="local")
    vecs = await embedder.embed_texts(chunks)
    store = await VectorStorePG.from_enterprise_db()
    doc_key = doc_id or (file.filename or "doc")
    for i, (chunk, v) in enumerate(zip(chunks, vecs)):
        await store.upsert_knowledge_chunk(
            tenant_id=tenant_id,
            doc_id=doc_key,
            chunk_ord=i,
            title=file.filename,
            category=category,
            source=f"upload://{file.filename}",
            text=chunk,
            traits={},
            tags=[category],
            acl=None,
            embedding=v,
        )
    return UploadResponse(tenant_id=tenant_id, doc_id=doc_key, chunks=len(chunks))

