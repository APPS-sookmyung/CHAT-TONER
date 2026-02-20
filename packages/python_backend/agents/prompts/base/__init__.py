# agents/prompts/base/__init__.py

from .system import SYSTEM_PROMPT
from .output_schema import OUTPUT_SCHEMA
from .few_shot_examples import FEW_SHOT_EXAMPLES

__all__ = ["SYSTEM_PROMPT", "OUTPUT_SCHEMA", "FEW_SHOT_EXAMPLES"]
