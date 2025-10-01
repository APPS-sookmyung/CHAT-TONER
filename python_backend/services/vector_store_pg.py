from typing import Any, Dict, List, Optional

# 조건부 import로 의존성 문제 해결
try:
    from services.enterprise_db_service import get_enterprise_db_service
    ENTERPRISE_DB_AVAILABLE = True
except ImportError:
    get_enterprise_db_service = None
    ENTERPRISE_DB_AVAILABLE = False


class VectorStorePG:
    def __init__(self, pool: Any):
        self.pool = pool

    @classmethod
    async def from_enterprise_db(cls):
        if not ENTERPRISE_DB_AVAILABLE or get_enterprise_db_service is None:
            raise RuntimeError("Enterprise DB service is not available. Please install required dependencies.")

        db = await get_enterprise_db_service()
        pool = getattr(db, "pool", db)
        return cls(pool)

    # ----- Style profile index -----
    async def upsert_style_profile(
        self,
        *,
        tenant_id: str,
        user_id: str,
        text: str,
        features: Dict[str, Any],
        traits: Dict[str, Any],
        embedding: List[float],
    ) -> None:
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO style_profile_index (tenant_id, user_id, text, features, traits, embedding)
                VALUES ($1, $2, $3, $4::jsonb, $5::jsonb, $6)
                ON CONFLICT (tenant_id, user_id)
                DO UPDATE SET
                  text = EXCLUDED.text,
                  features = EXCLUDED.features,
                  traits = EXCLUDED.traits,
                  embedding = EXCLUDED.embedding,
                  updated_at = now()
                """,
                tenant_id,
                user_id,
                text,
                features,
                traits,
                embedding,
            )

    async def search_style_profiles(
        self,
        *,
        tenant_id: str,
        query_embedding: List[float],
        top_k: int = 5,
        channel: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        # Clamp top_k to prevent abuse
        clamped_top_k = max(1, min(top_k, 100))

        where_clauses = ["tenant_id = $1"]
        params: List[Any] = [tenant_id, query_embedding]

        param_idx = 3
        if channel:
            where_clauses.append(f"(traits->>'primary_channel') = ${param_idx}")
            params.append(channel)
            param_idx += 1

        # Use parameterized query for LIMIT to prevent SQL injection
        params.append(clamped_top_k)
        limit_param = f"${param_idx}"

        sql = f"""
          SELECT user_id, text, features, traits, 1 - (embedding <=> $2) AS score
          FROM style_profile_index
          WHERE {' AND '.join(where_clauses)}
          ORDER BY embedding <=> $2
          LIMIT {limit_param}
        """
        rows: List[Dict[str, Any]] = []
        async with self.pool.acquire() as conn:
            r = await conn.fetch(sql, *params)
            for row in r:
                rows.append(
                    {
                        "user_id": row["user_id"],
                        "text": row["text"],
                        "features": row["features"],
                        "traits": row["traits"],
                        "score": float(row["score"]),
                    }
                )
        return rows

    # ----- Knowledge index -----
    async def upsert_knowledge_chunk(
        self,
        *,
        tenant_id: str,
        doc_id: str,
        chunk_ord: int,
        title: Optional[str],
        category: Optional[str],
        source: Optional[str],
        text: str,
        traits: Dict[str, Any],
        tags: List[str],
        acl: Optional[Dict[str, Any]],
        embedding: List[float],
    ) -> None:
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO knowledge_index (
                  tenant_id, doc_id, chunk_ord, title, category, source, text, traits, tags, acl, embedding
                )
                VALUES ($1,$2,$3,$4,$5,$6,$7,$8::jsonb,$9,$10::jsonb,$11)
                ON CONFLICT (tenant_id, doc_id, chunk_ord)
                DO UPDATE SET
                  title=EXCLUDED.title,
                  category=EXCLUDED.category,
                  source=EXCLUDED.source,
                  text=EXCLUDED.text,
                  traits=EXCLUDED.traits,
                  tags=EXCLUDED.tags,
                  acl=EXCLUDED.acl,
                  embedding=EXCLUDED.embedding,
                  updated_at=now()
                """,
                tenant_id,
                doc_id,
                chunk_ord,
                title,
                category,
                source,
                text,
                traits,
                tags,
                acl,
                embedding,
            )

    # ----- Final outputs index -----
    async def upsert_final_output(
        self,
        *,
        tenant_id: str,
        user_id: str,
        text: str,
        traits: Dict[str, Any],
        context: Dict[str, Any],
        embedding: List[float],
    ) -> None:
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO final_output_index (tenant_id, user_id, text, traits, context, embedding)
                VALUES ($1, $2, $3, $4::jsonb, $5::jsonb, $6)
                """,
                tenant_id,
                user_id,
                text,
                traits,
                context,
                embedding,
            )
