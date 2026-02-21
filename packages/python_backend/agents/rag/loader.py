from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# 실제 파일 위치: langchain_pipeline/data/documents/
RAG_DIR = Path("langchain_pipeline/data/documents")

STATIC_FILE_MAP = {
    "grammar_rules":     RAG_DIR / "grammar_rules.txt",
    "readability_rules": RAG_DIR / "readability_rules.txt",
    "business_style":    RAG_DIR / "business_style.txt",
    "negative_prompts":  RAG_DIR / "negative_prompts.txt",
    "ctx_email":         RAG_DIR / "email_guidelines.txt",
    "ctx_message":       RAG_DIR / "message_guidelines.txt",
    "ctx_report":        RAG_DIR / "report_guidelines",      # 확장자 없음
    "ctx_notice":        RAG_DIR / "notice_guidelines.txt",
    "ctx_minutes":       RAG_DIR / "meeting_minutes_guidelines",  # 확장자 없음
}

def load_static_files() -> dict[str, str | None]:
    """
    서버 시작 시 1번만 호출.
    실패해도 None으로 fallback — 서버 안 죽음.
    """
    loaded = {}
    for key, path in STATIC_FILE_MAP.items():
        try:
            loaded[key] = path.read_text(encoding="utf-8")
            logger.info(f"[Loader] {key}")
        except Exception as e:
            loaded[key] = None
            logger.warning(f"[Loader] {key} 로드 실패: {e}")
    return loaded