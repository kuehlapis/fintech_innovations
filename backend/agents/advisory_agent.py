import logging
from typing import Any

from backend.agents.base_agent import BaseAgent
from utils.config import getConfig

logger = logging.getLogger(__name__)


class AdvisoryAgent(BaseAgent):
    def __init__(self):
        cfg = getConfig()
        super().__init__(model=cfg.get_ollama_model())

    @staticmethod
    def _compute_wellness_score(
        diversification_score: float,
        sentiment_score: float,
        liquidity_ratio: float,
    ) -> int:
        sentiment_norm = (sentiment_score + 1.0) / 2.0
        raw = (
            diversification_score * 0.40
            + sentiment_norm * 0.30
            + liquidity_ratio * 0.30
        )
        return int(round(raw * 100))

    async def _generate_advisory_text(self, state: dict[str, Any]) -> str:
        asset_weights = state.get("asset_weights", {})
        total_value = state.get("total_value", 0.0)
        diversification_score = state.get("diversification_score", 0.0)
        sentiment_score = state.get("sentiment_score", 0.0)
        liquidity_ratio = state.get("liquidity_ratio", 0.0)
        wellness_score = state.get("_wellness_score", 0)
        headlines = state.get("news_headlines", [])

        allocation_lines = "\n".join(
            f"  - {ticker}: {weight*100:.1f}%"
            for ticker, weight in sorted(asset_weights.items(), key=lambda x: -x[1])
        )
        headline_sample = "\n".join(f"  - {h}" for h in headlines[:5])

        prompt = f"""You are a senior portfolio manager and financial advisor.
Analyse the following portfolio data and provide actionable, concise investment advice.

## Portfolio Summary
- Total Value: ${total_value:,.2f}
- Wellness Score: {wellness_score}/100
- Diversification Score: {diversification_score:.2f} (0=concentrated, 1=diversified)
- Liquidity Ratio: {liquidity_ratio:.2f}
- Market Sentiment: {sentiment_score:.2f} (-1=very negative, 0=neutral, +1=very positive)

## Asset Allocation
{allocation_lines if allocation_lines else "  No holdings data available."}

## Recent News Headlines
{headline_sample if headline_sample else "  No recent news available."}

## Instructions
1. Identify top 2-3 risks.
2. Suggest 2-3 actionable improvements.
3. Provide sentiment-adjusted outlook.
4. Keep response under 250 words.
5. Use plain English.
"""

        try:
            return (
                await self.chat_text(
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a professional financial advisor. Provide structured, practical investment advice.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    options={"temperature": 0.4},
                )
            ).strip()
        except Exception as exc:
            logger.error("[AdvisoryAgent] LLM error: %s", exc)
            return (
                "Unable to generate advisory text at this time. "
                "Please ensure your holdings are up-to-date and market data is available."
            )

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        diversification_score = state.get("diversification_score", 0.0)
        sentiment_score = state.get("sentiment_score", 0.0)
        liquidity_ratio = state.get("liquidity_ratio", 0.0)

        wellness_score = self._compute_wellness_score(
            diversification_score, sentiment_score, liquidity_ratio
        )

        advisory_text = await self._generate_advisory_text(
            {**state, "_wellness_score": wellness_score}
        )

        logger.info("[AdvisoryAgent] Wellness score: %d", wellness_score)
        return {**state, "wellness_score": wellness_score, "advisory_text": advisory_text}


_advisory_agent = AdvisoryAgent()


async def advisory_agent(state: dict[str, Any]) -> dict[str, Any]:
    return await _advisory_agent.run(state)
