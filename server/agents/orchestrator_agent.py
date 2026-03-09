from __future__ import annotations

import logging
import uuid
from typing import Any

from agents.registry import AgentRegistry
from agents.schemas import (
    AdvisoryRecommendation,
    FinalAgentDecision,
    IngestionRequest,
    IngestionResult,
    GuardrailResult,
    QuantSignal,
    SentimentResult,
)

logger = logging.getLogger(__name__)


class OrchestratorAgent:
    """Pipeline orchestrator that coordinates specialized agents."""

    def __init__(self, registry: AgentRegistry | None = None) -> None:
        self.registry = registry or AgentRegistry()
        self.ingestion_agent = self.registry.create("ingestion")
        self.sentiment_agent = self.registry.create("sentiment")
        self.quant_agent = self.registry.create("quant")
        self.advisory_agent = self.registry.create("advisory")
        self.guardrail_agent = self.registry.create("guardrail")

    async def run(self, request: IngestionRequest) -> FinalAgentDecision:
        request_id = str(uuid.uuid4())
        metadata: dict[str, Any] = {"request_id": request_id}

        logger.info("[Orchestrator] Start request %s", request_id)

        ingestion: IngestionResult = await self.ingestion_agent.run(request)
        sentiment: SentimentResult = await self.sentiment_agent.run(ingestion)
        quant: QuantSignal = await self.quant_agent.run(ingestion)
        advisory: AdvisoryRecommendation = await self.advisory_agent.run(
            ingestion, sentiment, quant
        )
        guardrail: GuardrailResult = await self.guardrail_agent.run(
            advisory, ingestion
        )

        logger.info("[Orchestrator] End request %s", request_id)

        return FinalAgentDecision(
            request_id=request_id,
            ingestion=ingestion,
            sentiment=sentiment,
            quant=quant,
            advisory=advisory,
            guardrail=guardrail,
            metadata=metadata,
        )
