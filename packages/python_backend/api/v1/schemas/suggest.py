from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class RewriteContext(BaseModel):
    audience: Optional[List[str]] = None  # e.g., ["executives", "team_leader"]
    situation: Optional[Literal["email", "meeting_minutes", "report", "chat", "other"]] = None
    purpose: Optional[str] = None  # e.g., approval_request, executive_briefing
    extras: Optional[Dict[str, Any]] = None  # subject_hint, urgency, etc.


class FeedbackItem(BaseModel):
    id: str
    type: Literal["grammar", "clarity", "tone", "policy", "term", "protocol"]
    note: Optional[str] = None
    before: Optional[str] = None
    after: Optional[str] = None
    span: Optional[Dict[str, int]] = None  # {start, end} (optional)


class TermSuggestion(BaseModel):
    id: str
    found: str
    replacement: str
    reason: Optional[str] = None
    source: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)


class SuggestRewriteRequest(BaseModel):
    text: str
    traits: Dict[str, Any]
    context: Optional[RewriteContext] = None
    feedback: Optional[List[FeedbackItem]] = None
    term_suggestions: Optional[List[TermSuggestion]] = None
    options: Optional[Dict[str, Any]] = None  # {strict_policy: bool, return_diff: bool}


class SuggestRewriteResponse(BaseModel):
    summary: Optional[str] = None
    revised_text: str
    grammar: Dict[str, Any]
    protocol: Dict[str, Any]
    citations: Optional[Dict[str, Any]] = None
    change_log: Optional[Dict[str, Any]] = None


# --- Finalize (apply good/bad decisions and persist) ---

class DecisionItem(BaseModel):
    id: str
    decision: Literal["good", "bad"]
    before: Optional[str] = None
    after: Optional[str] = None


class SuggestFinalizeRequest(BaseModel):
    tenant_id: str
    user_id: str
    text: str
    traits: Dict[str, Any]
    context: Optional[RewriteContext] = None
    grammar_choices: Optional[List[DecisionItem]] = None
    protocol_term_choices: Optional[List[DecisionItem]] = None
    options: Optional[Dict[str, Any]] = None  # {strict_policy: bool}


class SuggestFinalizeResponse(BaseModel):
    final_text: str
    grammar: Dict[str, Any]
    protocol: Dict[str, Any]
    citations: Optional[Dict[str, Any]] = None
    change_log: Optional[Dict[str, Any]] = None
    stored: Optional[Dict[str, Any]] = None
