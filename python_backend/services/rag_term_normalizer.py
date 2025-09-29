from typing import Any, Dict, Iterable, List, Optional
import os


def _iter_jsonl(path: str) -> Iterable[Dict[str, Any]]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    import json

                    yield json.loads(line)
                except Exception:
                    continue
    except FileNotFoundError:
        return []


class RAGTermNormalizer:
    def __init__(self, glossary_path: Optional[str] = None):
        self.glossary_path = glossary_path or os.path.join("data", "policy", "terminology_glossary.jsonl")
        self._entries: List[Dict[str, Any]] = list(_iter_jsonl(self.glossary_path))

    def suggest(self, *, text: str, channel: Optional[str] = None, audience: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        if not self._entries:
            return []
        au = set(audience or [])
        out: List[Dict[str, Any]] = []
        for e in self._entries:
            pref = e.get("preferred")
            discouraged = e.get("discouraged", []) or []
            ctx = e.get("context") or {}
            ctx_channels = set(ctx.get("channel", []) or [])
            ctx_audience = set(ctx.get("audience", []) or [])
            if ctx_channels and channel and channel not in ctx_channels:
                continue
            if ctx_audience and au and not (au & ctx_audience):
                continue
            for d in discouraged:
                if d and d in text:
                    out.append(
                        {
                            "id": f"term:{d}",
                            "found": d,
                            "replacement": pref,
                            "reason": "corporate glossary",
                            "source": {"title": "terminology_glossary", "category": "terminology"},
                            "confidence": 0.9,
                        }
                    )
        # Deduplicate by found/replacement
        dedup: Dict[str, Dict[str, Any]] = {}
        for s in out:
            key = s["found"] + "->" + s["replacement"]
            dedup[key] = s
        return list(dedup.values())

