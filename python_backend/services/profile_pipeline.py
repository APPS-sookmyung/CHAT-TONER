from typing import Any, Dict, Optional
from services.style_profile_service import build_style_profile
from services.embedding_service import EmbeddingService
from services.vector_store_pg import VectorStorePG


def answers_to_traits(answers: Dict[str, Any]) -> Dict[str, Any]:
    # Pass-through mapping. Customize ids/keys to your survey schema as needed.
    return dict(answers or {})


async def run_profile_pipeline(
    *, tenant_id: str, user_id: str, survey_answers: Dict[str, Any], store_vector: bool = True
) -> Dict[str, Any]:
    traits = answers_to_traits(survey_answers)
    profile = build_style_profile(user_id=user_id, tenant_id=tenant_id, traits=traits, use_llm=False)
    profile_text = profile.prompt

    stored = None
    if store_vector:
        embedder = EmbeddingService(provider="local")
        vec = (await embedder.embed_texts([profile_text]))[0]
        store = await VectorStorePG.from_enterprise_db()
        await store.upsert_style_profile(
            tenant_id=tenant_id,
            user_id=user_id,
            text=profile_text,
            features=profile.features.dict(),
            traits=traits,
            embedding=vec,
        )
        stored = {"tenant_id": tenant_id, "user_id": user_id}

    return {"traits": traits, "features": profile.features.dict(), "profile_text": profile_text, "stored": stored}

