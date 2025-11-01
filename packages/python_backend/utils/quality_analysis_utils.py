"""
Quality analysis utility functions
- Score extraction/calculation
- Mapping functions
- Generate default suggestions
"""
from typing import Dict, Any, List, Tuple, Optional


# ============ Extracting scores ============

def extract_formality_score(grammar: dict) -> float:
    """Formality score extraction"""
    korean_endings = grammar.get("korean_endings", {})
    if korean_endings.get("ending_ok"):
        return 85.0
    
    speech_map = {
        "합쇼체": 80.0,
        "해요체": 75.0,
        "의문형": 78.0,
        "평서/반말": 60.0
    }
    return speech_map.get(korean_endings.get("speech_level"), 65.0)


def extract_readability_score(grammar: dict) -> float:
    """Readability score extraction"""
    avg_len = grammar.get("metrics", {}).get("avg_sentence_len", 30)
    if avg_len < 20:
        return 90.0
    if avg_len < 30:
        return 85.0
    if avg_len < 50:
        return 75.0
    if avg_len < 80:
        return 65.0
    return 55.0


def extract_base_scores(rewrite_result: dict) -> dict:
    """Extract default scores from rewrite results"""
    grammar = rewrite_result.get("grammar", {})
    protocol = rewrite_result.get("protocol", {})
    
    return {
        "grammar_score": grammar.get("metrics", {}).get("grammar_score", 70.0),
        "formality_score": extract_formality_score(grammar),
        "readability_score": extract_readability_score(grammar),
        "protocol_score": protocol.get("metrics", {}).get("policy_score", 0.7) * 100
    }


# ============ Expectation-Gap  ============

def apply_expectation_gap(
    base_scores: dict,
    company_profile: Optional[dict]
) -> Tuple[dict, dict]:
    """
    Adjust scores based on company expectations.

    Args:
        base_scores: Dict of base scores.
        company_profile: Company profile (no adjustment if None).

    Returns:
        (adjusted_scores, adjustment_info)
    """
    if not company_profile:
        return base_scores, {"adjusted": False}
    
    company_style = company_profile.get("communication_style", "formal")
    expectations = {
        "strict": {"formality": 90, "protocol": 85},
        "formal": {"formality": 80, "protocol": 75},
        "friendly": {"formality": 70, "protocol": 65}
    }
    expected = expectations.get(company_style, expectations["formal"])
    
    formality_gap = max(0, expected["formality"] - base_scores["formality_score"])
    protocol_gap = max(0, expected["protocol"] - base_scores["protocol_score"])
    
    formality_penalty = formality_gap * 0.2
    protocol_penalty = protocol_gap * 0.3
    
    adjusted = {
        "grammar_score": base_scores["grammar_score"],
        "formality_score": max(0, base_scores["formality_score"] - formality_penalty),
        "readability_score": base_scores["readability_score"],
        "protocol_score": max(0, base_scores["protocol_score"] - protocol_penalty)
    }
    
    adjustment_info = {
        "adjusted": True,
        "company_style": company_style,
        "expected": expected,
        "gaps": {"formality_gap": formality_gap, "protocol_gap": protocol_gap},
        "penalties": {"formality_penalty": formality_penalty, "protocol_penalty": protocol_penalty}
    }
    
    return adjusted, adjustment_info


# ============ mapping ============

def map_audience(target: str) -> List[str]:
    """target → audience"""
    mapping = {
        "직속상사": ["executives"],
        "팀동료": ["team"],
        "타부서담당자": ["team"],
        "클라이언트": ["clients_vendors"],
        "외부협력업체": ["clients_vendors"],
        "후배신입": ["team"]
    }
    return mapping.get(target, ["team"])


def map_channel(context: str) -> str:
    """context → channel"""
    mapping = {
        "보고서": "report",
        "회의록": "meeting_minutes",
        "이메일": "email",
        "공지사항": "email",
        "메시지": "chat"
    }
    return mapping.get(context, "email")


# ============ Issues  ============

def summarize_issues(grammar: dict, protocol: dict) -> str:
    """Summarize analysis results for the LLM"""
    issues = []
    
    grammar_score = grammar.get("metrics", {}).get("grammar_score")
    if grammar_score is not None and grammar_score < 70:
        issues.append(f"- 전반적 문법 점수 낮음 ({grammar_score:.0f}점)")
    
    korean_endings = grammar.get("korean_endings", {})
    if not korean_endings.get("ending_ok"):
        issues.append(f"- 어미 격식: {korean_endings.get('speech_level', '부적절')}")
    
    banned = protocol.get("flags", {}).get("banned_terms", [])
    if banned:
        issues.append(f"- 금칙어 사용: {', '.join(banned[:3])}")
    
    missing = protocol.get("details", {}).get("missing_sections", [])
    if missing:
        issues.append(f"- 필수 섹션 누락: {', '.join(missing[:2])}")
    
    avg_len = grammar.get("metrics", {}).get("avg_sentence_len", 0)
    if avg_len > 50:
        issues.append(f"- 문장이 너무 김 (평균 {avg_len}자)")
    
    emoji_count = grammar.get("word_flags", {}).get("emoji_used", 0)
    if emoji_count > 0:
        issues.append(f"- 이모지 사용 ({emoji_count}개)")
    
    return "\n".join(issues) if issues else "주요 문제점 없음"


# ============ Generate default suggestions ============

def create_basic_suggestions(rewrite_result: dict) -> dict:
    """Generate default suggestions without an LLM"""
    protocol = rewrite_result.get("protocol", {})
    
    suggestions = {
        "grammar": [],
        "protocol": []
    }
    
    banned = protocol.get("flags", {}).get("banned_terms", [])
    for term in banned[:3]:
        suggestions["protocol"].append({
            "category": "프로토콜",
            "original": term,                           # violation → original
            "suggestion": "대체 표현 사용 필요",          # correction → suggestion
            "reason": "금칙어 사용 - 기업 정책 위반",
            "severity": "high"
        })
    
    missing = protocol.get("details", {}).get("missing_sections", [])
    for section in missing[:2]:
        suggestions["protocol"].append({
            "category": "프로토콜",
            "original": f"[{section} 섹션]",
            "suggestion": f"{section} 섹션 추가 권장",    # correction → suggestion
            "reason": f"필수 섹션 누락 - {section} 필요",
            "severity": "medium"
        })
    
    if not protocol.get("flags", {}).get("tone_consistent", True):
        suggestions["grammar"].append({
            "category": "톤",
            "original": "[전체 텍스트]",
            "suggestion": "격식 있는 표현으로 통일",
            "reason": "톤 일관성 - 비즈니스 커뮤니케이션 톤 유지"
        })
    
    return suggestions


# ============ Improvement priority ============

def determine_improvement_priority(scores: dict) -> List[str]:
    """Score-based improvement prioritization"""
    priorities = []
    
    if scores.get("protocol_score", 70) < 70:
        priorities.append("기업 프로토콜 준수")
    if scores.get("formality_score", 70) < 70:
        priorities.append("격식도 조정")
    if scores.get("grammar_score", 70) < 70:
        priorities.append("문법 개선")
    if scores.get("readability_score", 70) < 70:
        priorities.append("가독성 향상")
    
    return priorities or ["전반적 품질 향상"]


def identify_concerns(scores: dict) -> List[str]:
    """주요 개선점 식별 (determine_improvement_priority의 별칭)"""
    return determine_improvement_priority(scores)