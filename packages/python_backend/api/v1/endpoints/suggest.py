from fastapi import APIRouter, HTTPException
from typing import Any, Dict, List

from ..schemas.suggest import (
    SuggestRewriteRequest,
    SuggestRewriteResponse,
    SuggestFinalizeRequest,
    SuggestFinalizeResponse,
    FeedbackItem,
    TermSuggestion,
)
from services.rewrite_service import rewrite_text
from services.embedding_service import EmbeddingService
from services.vector_store_pg import VectorStorePG


router = APIRouter(tags=["suggest"])


@router.post("/rewrite", response_model=SuggestRewriteResponse)
async def suggest_rewrite(req: SuggestRewriteRequest) -> SuggestRewriteResponse:
    if not req.text:
        raise HTTPException(status_code=400, detail="text is required")

    result: Dict[str, Any] = rewrite_text(
        text=req.text,
        traits=req.traits,
        context=(req.context.dict() if req.context else {}),
        feedback=[fb.dict() for fb in (req.feedback or [])],
        term_suggestions=[ts.dict() for ts in (req.term_suggestions or [])],
        options=(req.options or {}),
    )
    return SuggestRewriteResponse(**result)


@router.post("/finalize", response_model=SuggestFinalizeResponse)
async def suggest_finalize(req: SuggestFinalizeRequest) -> SuggestFinalizeResponse:
    if not (req.text and req.tenant_id and req.user_id):
        raise HTTPException(status_code=400, detail="tenant_id, user_id and text are required")

    # Build accepted feedback and term suggestions from decisions
    accepted_feedback: List[FeedbackItem] = []
    for d in (req.grammar_choices or []):
        if d.decision == "good" and d.before and d.after:
            accepted_feedback.append(FeedbackItem(id=d.id, type="grammar", before=d.before, after=d.after))

    accepted_terms: List[TermSuggestion] = []
    for d in (req.protocol_term_choices or []):
        if d.decision == "good" and d.before and d.after:
            accepted_terms.append(TermSuggestion(id=d.id, found=d.before, replacement=d.after, confidence=1.0))

    res: Dict[str, Any] = rewrite_text(
        text=req.text,
        traits=req.traits,
        context=(req.context.dict() if req.context else {}),
        feedback=[fb.dict() for fb in accepted_feedback],
        term_suggestions=[ts.dict() for ts in accepted_terms],
        options=(req.options or {"strict_policy": True}),
    )

    # Persist final output to vector DB for future retrieval
    embedder = EmbeddingService(provider="local")  # switch to "openai" when configured
    vec = (await embedder.embed_texts([res["revised_text"]]))[0]
    store = await VectorStorePG.from_enterprise_db()
    ctx = (req.context.dict() if req.context else {})
    await store.upsert_final_output(
        tenant_id=req.tenant_id,
        user_id=req.user_id,
        text=res["revised_text"],
        traits=req.traits,
        context=ctx,
        embedding=vec,
    )

    return SuggestFinalizeResponse(
        final_text=res["revised_text"],
        grammar=res["grammar"],
        protocol=res["protocol"],
        citations=res.get("citations"),
        change_log=res.get("change_log"),
        stored={"tenant_id": req.tenant_id, "user_id": req.user_id},
    )
