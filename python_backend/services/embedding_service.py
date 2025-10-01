from typing import List, Optional
import math


class EmbeddingService:
    """텍스트 임베딩 서비스 클래스"""

    def __init__(self, provider: str = "local", model: Optional[str] = None):
        """
        임베딩 서비스 초기화

        Args:
            provider: 임베딩 제공자 ("local" 또는 "openai")
            model: 사용할 모델명 (기본값은 제공자에 따라 자동 설정)
        """
        self.provider = provider
        self.model = model or ("text-embedding-3-small" if provider == "openai" else "local-384")

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        텍스트 목록을 벡터로 임베딩

        Args:
            texts: 임베딩할 텍스트 목록

        Returns:
            각 텍스트에 대한 임베딩 벡터 목록

        Raises:
            RuntimeError: OpenAI 임베딩이 설정되지 않은 경우
        """
        if self.provider == "openai":
            # Placeholder: integrate your OpenAI client here.
            raise RuntimeError("OpenAI embedding not configured in this environment.")
        # Local deterministic stub for development: 384-dim sparse vectors
        dims = 384
        out: List[List[float]] = []
        for t in texts:
            v = [0.0] * dims
            v[0] = min(1.0, max(0.0, len(t) / 2000.0))
            norm = math.sqrt(sum(x * x for x in v)) or 1.0
            out.append([x / norm for x in v])
        return out

