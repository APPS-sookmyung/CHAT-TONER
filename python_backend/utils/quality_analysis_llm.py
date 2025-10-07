"""
LLM-based suggestion generation
- Uses both Agent and Service
- Unified prompt and parsing
"""
import logging
import json
import re
from typing import Dict, Any, List, Optional
from utils.quality_analysis_utils import summarize_issues, create_basic_suggestions

logger = logging.getLogger('chattoner.quality_analysis_llm')


async def generate_suggestions_with_llm(
    rag_service,
    text: str,
    rewrite_result: dict,
    target_audience: str,
    context: str,
    company_profile: Optional[Dict[str, Any]] = None,
    max_grammar: int = 5,
    max_protocol: int = 5
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Generate concrete suggestions with an LLM.

    Args:
        rag_service: RAG service.
        text: Original text.
        rewrite_result: Result from rewrite_text().
        target_audience: Target audience.
        context: Context of use.
        company_profile: Company profile (optional).
        max_grammar: Maximum number of grammar suggestions.
        max_protocol: Maximum number of protocol suggestions.

    Returns:
        {"grammar": [...], "protocol": [...]}
    """


    
    grammar = rewrite_result.get("grammar", {})
    protocol = rewrite_result.get("protocol", {})
    issues_summary = summarize_issues(grammar, protocol)
    company_style = company_profile.get("communication_style", "formal") if company_profile else "formal"
    prompt = f"""다음 텍스트의 문제점을 기반으로 구체적인 수정 제안을 생성해주세요.

원문:
{text[:300]}{"..." if len(text) > 300 else ""}

대상: {target_audience}
상황: {context}
기업 스타일: {company_style}

감지된 문제:
{issues_summary}

다음 JSON 형식으로만 응답:
{{
    "grammar_suggestions": [
        {{
            "original": "원문에서 문제 있는 구체적 표현",
            "suggestion": "수정된 표현",
            "reason": "수정 이유"
        }}
    ],
    "protocol_suggestions": [
        {{
            "original": "위반 표현",
            "suggestion": "수정 방안",
            "reason": "위반 이유 설명",
            "severity": "high|medium|low"
        }}
    ]
}}

최대 5개씩만 제안하세요."""
    
    # LLM call
    try:
        result = await rag_service.ask_generative_question(
            query=prompt,
            context="기업 텍스트 개선 제안"
        )
        
        if result and result.get("success"):
            # JSON parsing
            json_match = re.search(r'\{[\s\S]*\}', result["answer"])
            if json_match:
                suggestions_data = json.loads(json_match.group())
            else:
                suggestions_data = json.loads(result["answer"])
            
            # Formatting
            return {
                "grammar": [
                    {
                        "category": "문법",
                        "original": s.get("original", ""),
                        "suggestion": s.get("suggestion", ""),
                        "reason": s.get("reason", "")
                    }
                    for s in suggestions_data.get("grammar_suggestions", [])[:max_grammar]
                ],
                "protocol": [
                    {
                        "category": "프로토콜",
                        "original": s.get("original", ""),          # violation → original
                        "suggestion": s.get("suggestion", ""),      # correction → suggestion
                        "reason": s.get("reason", ""),
                        "severity": s.get("severity", "medium")
                    }
                    for s in suggestions_data.get("protocol_suggestions", [])[:max_protocol]
                ]
            }
    
    except Exception as e:
        logger.error(f"LLM 제안 생성 실패: {e}")
    
    # Default suggestions on LLM failure
    return create_basic_suggestions(rewrite_result)