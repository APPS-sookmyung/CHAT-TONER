from agents.rag.loader import load_static_files
from agents.rag.protocol_retriever import ProtocolRetriever
import logging

logger = logging.getLogger(__name__)

# 서버 전역 상태
static_files: dict[str, str | None] = {}
protocol_retriever: ProtocolRetriever = ProtocolRetriever()


def init_app_state():
    """
    서버 시작 시 1번만 호출 (main.py lifespan).
    """
    global static_files

    logger.info("[State] static 파일 로드 시작")
    static_files = load_static_files()

    logger.info("[State] PDF 인덱스 초기화 시작")
    protocol_retriever.initialize()

    logger.info("[State] 초기화 완료")
