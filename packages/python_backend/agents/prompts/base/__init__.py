# agents/prompts/base/__init__.py

from .system import SYSTEM_PROMPT
from .output_schema import OUTPUT_SCHEMA
from .few_shot_examples import (
    FEW_SHOT_EXAMPLES,
    FEW_SHOT_GRAMMAR,
    FEW_SHOT_FORMALITY,
    FEW_SHOT_PROTOCOL,
    FEW_SHOT_FINAL_TEXT,
    FEW_SHOT_SUMMARY,
    FEW_SHOT_ORIGINAL,
)

__all__ = [
    "SYSTEM_PROMPT",
    "OUTPUT_SCHEMA",
    "FEW_SHOT_EXAMPLES",
    "FEW_SHOT_GRAMMAR",
    "FEW_SHOT_FORMALITY",
    "FEW_SHOT_PROTOCOL",
    "FEW_SHOT_FINAL_TEXT",
    "FEW_SHOT_SUMMARY",
    "FEW_SHOT_ORIGINAL",
]
