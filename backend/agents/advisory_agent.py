import logging
from typing import Iterable

from agents.base_agent import BaseAgent
from agents.schemas import AdvisoryRecommendation, IngestionResult, QuantSignal, SentimentResult

logger = logging.getLogger(__name__)


class AdvisoryAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(agent_type="advisory")

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

    @staticmethod
    def _format_list(values: Iterable[str]) -> str:
        return "\n".join(f"- {value}" for value in values if value)

    def _build_input(
        self,
        ingestion: IngestionResult,
        sentiment: SentimentResult,
        quant: QuantSignal,
    ) -> str:
        allocation_lines = self._format_list(
            [
                f"{ticker}: {weight * 100:.1f}%"
                for ticker, weight in sorted(
                    quant.asset_weights.items(), key=lambda x: -x[1]
                )
            ]
        )
        headlines = self._format_list(ingestion.news_headlines[:5])
        wellness_score = self._compute_wellness_score(
            quant.diversification_score,
            sentiment.sentiment_score,
            quant.liquidity_ratio,
        )

        return (
            "Portfolio Summary\n"
            f"- Total Value: ${quant.total_value:,.2f}\n"
            f"- Wellness Score: {wellness_score}/100\n"
            f"- Diversification Score: {quant.diversification_score:.2f}\n"
            f"- Liquidity Ratio: {quant.liquidity_ratio:.2f}\n"
            f"- Sentiment Score: {sentiment.sentiment_score:.2f}\n\n"
            "Asset Allocation\n"
            f"{allocation_lines or '- No holdings data available.'}\n\n"
            "Recent News\n"
            f"{headlines or '- No recent news available.'}"
        )

    def _fallback_recommendation(self, quant: QuantSignal) -> AdvisoryRecommendation:
        summary = (
            "Portfolio review completed. Focus on diversification and liquidity "
            "while monitoring market conditions."
        )
        risks = [
            "Concentration risk" if quant.diversification_score < 0.4 else "",
            "Liquidity constraints" if quant.liquidity_ratio < 0.5 else "",
        ]
        actions = [
            "Review allocation targets and rebalance if concentrated.",
            "Keep a cash buffer for near-term needs.",
        ]
        outlook = "Neutral outlook with emphasis on risk management."
        rationale = "Generated without LLM due to missing configuration."
        return AdvisoryRecommendation(
            summary=summary,
            risks=[r for r in risks if r],
            actions=actions,
            outlook=outlook,
            confidence=0.3,
            rationale=rationale,
        )

    async def run(
        self,
        ingestion: IngestionResult,
        sentiment: SentimentResult,
        quant: QuantSignal,
    ) -> AdvisoryRecommendation:
        input_text = self._build_input(ingestion, sentiment, quant)

        if not self.client:
            return self._fallback_recommendation(quant)

        try:
            recommendation = self.run_structured(input_text, AdvisoryRecommendation)
            if not recommendation.summary:
                recommendation.summary = "Portfolio analysis completed."
            if not recommendation.rationale:
                recommendation.rationale = "Generated from portfolio metrics and sentiment."
            return recommendation
        except Exception as exc:
            logger.error("[AdvisoryAgent] LLM error: %s", exc)
            return self._fallback_recommendation(quant)
