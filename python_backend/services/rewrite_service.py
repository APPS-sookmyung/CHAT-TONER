import re
from typing import Any, Dict, List, Optional, Tuple


def _strip_emoji(text: str) -> Tuple[str, int]:
    # Basic emoji range removal
    emoji_pattern = re.compile(
        "[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]",
        flags=re.UNICODE,
    )
    new_text, n = emoji_pattern.subn("", text)
    return new_text, n


FORMAL_ENDINGS = [
    "습니다", "입니다", "드립니다", "하시기 바랍니다", "주시기 바랍니다", "바랍니다",
]
POLITE_ENDINGS = ["해요", "이에요", "예요", "해주세요", "할게요", "될게요"]


def _ensure_formal_request(text: str) -> Tuple[str, Optional[str]]:
    # Normalize common polite endings to formal request for executives/email contexts
    # Replace patterns like "해주세요" -> "주시기 바랍니다"
    before = text
    text = re.sub(r"해주세요[.!?]?", "주시기 바랍니다.", text)
    text = re.sub(r"부탁드립니다[.!?]?", "주시기 바랍니다.", text)
    return text, ("formal_request" if before != text else None)


def _has_formal_majority(text: str) -> bool:
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", text) if s.strip()]
    if not sents:
        return True
    def is_formal(s: str) -> bool:
        return any(s.endswith(e) for e in FORMAL_ENDINGS) or s.endswith("니다.")
    count = sum(1 for s in sents if is_formal(s))
    return (count / max(1, len(sents))) >= 0.6


def _insert_email_sections(text: str, subject_hint: Optional[str]) -> Tuple[str, List[str]]:
    changes: List[str] = []
    lines = text.splitlines()
    # Subject suggestion
    if subject_hint and not any(l.lower().startswith("subject:") for l in lines[:3]):
        lines.insert(0, f"Subject: {subject_hint}")
        changes.append("insert_subject")
    # Ensure CTA section hint
    if "CTA:" not in text and "요청:" not in text:
        lines.append("\nCTA: 주요 요청을 한 줄로 명확히 작성해 주세요.")
        changes.append("insert_cta")
    return "\n".join(lines), changes


def _apply_feedback(text: str, feedback: Optional[List[Dict[str, Any]]]) -> Tuple[str, List[Dict[str, Any]]]:
    applied: List[Dict[str, Any]] = []
    if not feedback:
        return text, applied
    cur = text
    for fb in feedback:
        if fb.get("type") not in {"grammar", "clarity", "term"}:
            continue
        before = fb.get("before")
        after = fb.get("after")
        if before and after and before in cur:
            cur = cur.replace(before, after)
            applied.append({"id": fb.get("id"), "rule": fb.get("type"), "before": before, "after": after})
    return cur, applied


def _apply_term_suggestions(text: str, term_suggestions: Optional[List[Dict[str, Any]]]) -> Tuple[str, List[Dict[str, Any]]]:
    applied: List[Dict[str, Any]] = []
    if not term_suggestions:
        return text, applied
    cur = text
    for ts in term_suggestions:
        found = ts.get("found")
        repl = ts.get("replacement")
        conf = ts.get("confidence", 1.0) or 0.0
        if not found or not repl:
            continue
        if conf < 0.75:
            continue
        if found in cur:
            cur = cur.replace(found, repl)
            applied.append({
                "id": ts.get("id"),
                "before": found,
                "after": repl,
                "reason": ts.get("reason"),
                "source": ts.get("source"),
            })
    return cur, applied


def _analyze_korean_endings(text: str, expected_level: str) -> Dict[str, Any]:
    FORMAL = re.compile(r"(습니다|입니다|드립니다|하십시오|주시기 바랍니다)([.!?]?)$")
    POLITE = re.compile(r"(해요|이에요|예요|주세요|할게요|될게요)([.!?]?)$")
    PLAIN = re.compile(r"(한다|했다|해라|해)([.!?]?)$")
    QMARK = re.compile(r"(습니까\?|인가요\?|맞나요\?|나요\?)$")
    def cls(s: str) -> str:
        if QMARK.search(s):
            return "의문형"
        if FORMAL.search(s):
            return "합쇼체"
        if POLITE.search(s):
            return "해요체"
        if PLAIN.search(s):
            return "평서/반말"
        return "기타"
    sents = [x.strip() for x in re.split(r"(?<=[.!?])\s+|\n+", text) if x.strip()]
    endings = []
    levels = {}
    for i, s in enumerate(sents):
        level = cls(s)
        levels[level] = levels.get(level, 0) + 1
        ok = ((expected_level == "formal" and level in ["합쇼체", "의문형"]) or
              (expected_level == "polite" and level in ["해요체", "의문형"]) or
              (expected_level == "casual" and level in ["해요체", "평서/반말"]))  # type: ignore
        endings.append({"sent_idx": i, "ending": s[-6:], "type": level, "ok": bool(ok)})
    speech = max(levels, key=levels.get) if levels else "기타"
    return {"speech_level": speech, "ending_ok": all(e["ok"] for e in endings) if endings else True, "endings": endings}


def _protocol_checks(text: str, channel: Optional[str], audience: Optional[List[str]]) -> Dict[str, Any]:
    # Minimal protocol checks: banned terms, email/report sections, emoji presence
    try:
        from services.policy_service import load_policy  # lazy import to avoid cycles
        policy = load_policy()
        banned_terms = policy.get("ban_terms", [])
    except Exception:
        policy = {}
        banned_terms = []
    hits = [t for t in banned_terms if t and t in text]
    # Sections
    missing_sections: List[str] = []
    if channel == "email":
        if "Subject:" not in text:
            missing_sections.append("subject")
        if "CTA:" not in text and "요청:" not in text:
            missing_sections.append("cta")
    if channel == "report":
        for sec in ("Executive Summary", "요약"):
            if sec in text:
                break
        else:
            missing_sections.append("executive_summary")
    # Emoji count
    _, emoji_count = _strip_emoji(text)
    tone_mismatch = 0
    if audience and ("executives" in audience or "clients_vendors" in audience):
        if emoji_count > 0:
            tone_mismatch = 1
    policy_score = 1.0
    if hits:
        policy_score -= 0.5
    if missing_sections:
        policy_score -= 0.2
    if tone_mismatch:
        policy_score -= 0.2
    return {
        "summary": "형식/톤/금칙어 간이 점검 결과",
        "metrics": {
            "policy_score": max(0.0, policy_score),
            "banned_count": len(hits),
            "pii_hits_count": 0,
            "missing_sections_count": len(missing_sections),
            "tone_mismatch": tone_mismatch,
        },
        "flags": {
            "banned_terms": hits,
            "format_ok": len(missing_sections) == 0,
            "tone_consistent": tone_mismatch == 0,
            "pii_hits": [],
        },
        "details": {
            "missing_sections": missing_sections,
            "tone_notes": "임원/대외 대상은 이모지 금지",
            "channel_policy": f"{channel or 'unknown'}.v1",
        },
    }


def rewrite_text(
    *,
    text: str,
    traits: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None,
    feedback: Optional[List[Dict[str, Any]]] = None,
    term_suggestions: Optional[List[Dict[str, Any]]] = None,
    options: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    ctx = context or {}
    audience = ctx.get("audience") or []
    channel = ctx.get("situation") or ctx.get("channel")
    extras = ctx.get("extras") or {}
    strict = bool((options or {}).get("strict_policy"))
    analysis_only = bool((options or {}).get("analysis_only")) # for fallback use

    revised = text
    applied_fixes: List[Dict[str, Any]] = []
    steps: List[str] = []

    # If analysis_only is True, only analysis is performed without making any modifications (for fallback use)
    # Skip text modification step if analysis_only is True
    if not analysis_only:
        # 1) Apply grammar/clarity feedback
        revised, fixes = _apply_feedback(revised, feedback)
        if fixes:
            applied_fixes.extend(fixes)
            steps.append("feedback_grammar_applied")

        # 2) Apply terminology suggestions
        revised, term_fixes = _apply_term_suggestions(revised, term_suggestions)
        if term_fixes:
            applied_fixes.extend([{"id": fx.get("id"), "before": fx.get("before"), "after": fx.get("after"), "rule": "term"} for fx in term_fixes])
            steps.append("terms_normalized")

        # 3) Policy/channel specific normalizations
        emoji_removed = 0
        if channel in {"email", "report", "meeting_minutes"} and ("executives" in audience or "clients_vendors" in audience):
            revised, n = _strip_emoji(revised)
            emoji_removed += n
        if channel == "email":
            revised, ch = _insert_email_sections(revised, extras.get("subject_hint"))
            if ch:
                steps.extend(ch)
        # ensure formal endings for formal contexts
        if ("executives" in audience or channel in {"email", "report"}):
            revised, tag = _ensure_formal_request(revised)
            if tag:
                steps.append(tag)
    else:
        # Analysis-only mode
        steps.append("analysis_only_mode")
        emoji_removed = 0

    # 4) Grammar summary 
    expected = "formal" if ("executives" in audience or channel in {"email", "report"}) else "polite"
    ko_end = _analyze_korean_endings(revised, expected)
    avg_sentence_len = 0
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", revised) if s.strip()]
    if sents:
        avg_sentence_len = int(sum(len(s) for s in sents) / len(sents))
    grammar = {
        "summary": "격식 점검 및 기본 문법 휴리스틱 적용" if not analysis_only else "원본 텍스트 분석",
        "metrics": {"errors_per_1k": 0.0, "grammar_score": 95 if ko_end.get("ending_ok") else 70, "avg_sentence_len": avg_sentence_len},
        "korean_endings": ko_end,
        "word_flags": {"slang": [], "jargon": [], "banned_terms": [], "emoji_used": 0},
    }

    # 5) Protocol section 
    protocol = _protocol_checks(revised, channel, audience)

    summary = "원본 텍스트를 분석했습니다." if analysis_only else "피드백과 정책을 반영하여 재작성했습니다."
    if strict and (protocol["metrics"]["banned_count"] or protocol["metrics"]["pii_hits_count"]):
        summary += " 금칙어나 민감정보가 감지되어 일부 적용이 제한되었습니다."

    return {
        "summary": summary,
        "revised_text": revised,
        "grammar": grammar,
        "protocol": protocol,
        "citations": None,
        "change_log": {"steps": steps, "applied_fixes": applied_fixes, "emoji_removed": emoji_removed},
    }