# agents/prompts/builder.py

from .base.system import SYSTEM_PROMPT
from .base.output_schema import OUTPUT_SCHEMA
from .base.few_shot_examples import FEW_SHOT_EXAMPLES
from .modifiers.target import TARGET_MODIFIERS, FORMALITY_CRITERIA
from .modifiers.context import CONTEXT_MODIFIERS
from .rag_sections.grammar import get_grammar_section
from .rag_sections.formality import get_formality_section
from .rag_sections.protocol import get_protocol_section


def build_prompt(
    text: str,
    target: str,
    context: str,
    grammar_rules: str | None = None,
    readability_rules: str | None = None,
    business_style: str | None = None,
    negative_prompts: str | None = None,
    rag_chunks: list[str] | None = None,
    company_name: str | None = None,
) -> tuple[str, str]:
    """
    Returns:
        tuple[system_prompt, user_prompt]
    """

    grammar_section = get_grammar_section(
        grammar_rules=grammar_rules,
        readability_rules=readability_rules
    )

    formality_section = get_formality_section(
        business_style=business_style,
        negative_prompts=negative_prompts,
        target=target,
        formality_criteria=FORMALITY_CRITERIA.get(target, {"ideal": 70, "min": 50})
    )

    protocol_section = get_protocol_section(
        rag_chunks=rag_chunks,
        company_name=company_name,
        target=target,
        context=context
    )

    user_prompt = f"""
{FEW_SHOT_EXAMPLES}

{grammar_section}

{formality_section}

{protocol_section}

## 수신자
{TARGET_MODIFIERS[target]}

## 문서 유형
{CONTEXT_MODIFIERS[context]}

## 분석할 원문
{text}

## 출력 형식
{OUTPUT_SCHEMA}
"""

    return SYSTEM_PROMPT, user_prompt