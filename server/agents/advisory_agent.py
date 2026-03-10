# advisory_agent.py
import json
import logging

from agents.base_agent import BaseAgent
from models.schemas import AdvisoryRecommendation, IngestionResult, QuantSignal, SentimentResult

logger = logging.getLogger(__name__)


class AdvisoryAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(agent_type="advisory")

    async def run(
        self,
        ingestion: IngestionResult,
        sentiment: SentimentResult,
        quant: QuantSignal,
    ) -> AdvisoryRecommendation:
        # Deterministic fallback first
        risks: list[str] = []
        actions: list[str] = []
        warnings = ["Advisory only. No trade is executed automatically."]

        if quant.diversification_score < 0.4:
            risks.append("Portfolio concentration risk is elevated.")
            actions.append("Diversify concentrated positions across asset classes and sectors.")
        if quant.liquidity_ratio < 0.35:
            risks.append("Liquidity profile is low.")
            actions.append("Increase allocation to liquid assets to improve flexibility.")
        if sentiment.sentiment_score < -0.2:
            risks.append("Current market sentiment is negative for parts of the portfolio.")
            actions.append("Review risk controls and reduce highly volatile exposure where needed.")

        fallback = AdvisoryRecommendation(
            summary=(
                f"Portfolio health from diversification ({quant.diversification_score:.2f}), "
                f"liquidity ({quant.liquidity_ratio:.2f}), and sentiment ({sentiment.sentiment_score:.2f})."
            ),
            risks=risks,
            actions=actions or ["Maintain allocation and monitor changes periodically."],
            outlook="Neutral-to-cautious",
            confidence=0.70,
            rationale="Recommendation combines concentration, liquidity, and sentiment context.",
            warnings=warnings,
        )

        if not self.client:
            return fallback

        try:
            llm = self.run_structured(
                input_text=(
                    "Generate a portfolio recommendation with concise rationale and practical actions.\n"
                    + json.dumps(
                        {
                            "ingestion": ingestion.model_dump(),
                            "quant": quant.model_dump(),
                            "sentiment": sentiment.model_dump(),
                        }
                    )
                ),
                schema=AdvisoryRecommendation,
            )

            if not llm.warnings:
                llm.warnings = warnings
            if not llm.actions:
                llm.actions = fallback.actions
            if not llm.summary:
                llm.summary = fallback.summary
            if not llm.rationale:
                llm.rationale = fallback.rationale

            return llm
        except Exception as exc:
            logger.warning("[advisory] LLM recommendation failed, using fallback: %s", exc)
            return fallback