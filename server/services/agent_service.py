from __future__ import annotations

import logging

from agents.orchestrator_agent import OrchestratorAgent
from agents.schemas import FinalAgentDecision, IngestionRequest
from utils.logger import configure_logging

logger = logging.getLogger(__name__)


class AgentService:
    """Service layer entry point for the agent pipeline."""

    def __init__(self) -> None:
        configure_logging()
        self.orchestrator = OrchestratorAgent()

    async def run_portfolio_analysis(self, request: IngestionRequest) -> FinalAgentDecision:
        logger.info("[AgentService] Running portfolio analysis")
        return await self.orchestrator.run(request)
