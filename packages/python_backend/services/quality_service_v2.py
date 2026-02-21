from agents.quality_analysis_agent_v2 import QualityAnalysisAgent
from agents.base_agent import BaseAgentResult
from core.state import static_files, protocol_retriever
import logging

logger = logging.getLogger(__name__)


class QualityService:

    def __init__(self):
        self.agent = QualityAnalysisAgent(retriever=protocol_retriever)
        self.agent.initialize()

    async def analyze(
        self,
        text: str,
        target: str,
        context: str,
        company_id: str | None = None,
    ) -> BaseAgentResult:
        return await self.agent.execute(
            text=text,
            target=target,
            context=context,
            company_id=company_id,
            grammar_rules=static_files.get("grammar_rules"),
            readability_rules=static_files.get("readability_rules"),
            business_style=static_files.get("business_style"),
            negative_prompts=static_files.get("negative_prompts"),
        )