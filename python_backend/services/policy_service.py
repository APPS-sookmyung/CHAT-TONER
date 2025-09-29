import json
import os
from functools import lru_cache
from typing import Any, Dict


POLICY_PATH = os.getenv("POLICY_FILE", os.path.join("data", "policy", "policy.json"))


@lru_cache(maxsize=1)
def load_policy() -> Dict[str, Any]:
    try:
        with open(POLICY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # Minimal default
        return {
            "ban_terms": [],
            "ban_regex": [],
            "dlp_patterns": {},
            "required_sections_by_channel": {
                "email": ["subject", "summary", "cta"],
                "report": ["executive_summary"],
                "meeting_minutes": ["agenda", "decisions", "action_items"],
            },
            "tone_rules": {
                "executives": {"emoji": False, "formality_min": 4}
            },
        }

