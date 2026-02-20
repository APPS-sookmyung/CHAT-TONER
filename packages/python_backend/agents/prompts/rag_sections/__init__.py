# agents/prompts/rag_sections/__init__.py

from .grammar import get_grammar_section
from .formality import get_formality_section
from .protocol import get_protocol_section

__all__ = ["get_grammar_section", "get_formality_section", "get_protocol_section"]
