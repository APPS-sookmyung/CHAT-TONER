from typing import Any, Dict, Optional
from services.style_profile_service import build_style_profile, extract_style_features_from_survey # Added import
from services.embedding_service import EmbeddingService
from services.vector_store_pg import VectorStorePG


def answers_to_traits(answers: Dict[str, Any]) -> Dict[str, Any]:
    # Pass-through mapping. Customize ids/keys to your survey schema as needed.
    return dict(answers or {})


async def run_profile_pipeline(
    *, tenant_id: str, user_id: str, survey_answers: Dict[str, Any], store: Optional[VectorStorePG], store_vector: bool = True
) -> Dict[str, Any]:
    # Use extract_style_features_from_survey to get the numerical features
    style_features = extract_style_features_from_survey(survey_answers)
    
    # Pass the extracted features (as a dict) to build_style_profile
    # build_style_profile expects a dict for traits, so convert StyleFeatures to dict
    profile = build_style_profile(user_id=user_id, tenant_id=tenant_id, traits=style_features.dict(), use_llm=False)
    profile_text = profile.prompt

    stored = None
    if store_vector and store is not None:
        embedder = EmbeddingService(provider="local")
        vec = (await embedder.embed_texts([profile_text]))[0]
        await store.upsert_style_profile(
            tenant_id=tenant_id,
            user_id=user_id,
            text=profile_text,
            features=profile.features.dict(),
            traits=style_features.dict(), # Use the extracted style_features here
            embedding=vec,
        )
        stored = {"tenant_id": tenant_id, "user_id": user_id}

    return {"traits": style_features.dict(), "features": profile.features.dict(), "profile_text": profile_text, "stored": stored}

