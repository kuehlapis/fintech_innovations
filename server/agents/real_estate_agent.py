import json
import logging

from agents.base_agent import BaseAgent
from models.schemas import IngestionResult, QuantSignal

logger = logging.getLogger(__name__)


class RealEstateAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(agent_type="real_estate")

    def _baseline(self, ingestion: IngestionResult) -> QuantSignal:
        holdings = [h for h in ingestion.holdings if h.asset_type == "real_estate"]
        if not holdings:
            return QuantSignal()

        total = 0.0
        values = {}
        for idx, h in enumerate(holdings):
            key = h.ticker or f"re_{idx}"
            v = float(h.value or 0.0)
            if v <= 0:
                v = float(h.quantity or 0.0) * 100000.0
            v = max(v, 0.0)
            values[key] = v
            total += v

        if total <= 0:
            return QuantSignal()

        weights = {k: v / total for k, v in values.items()}
        hhi = sum(w * w for w in weights.values())
        n = max(len(weights), 1)
        diversification = 1.0 if n == 1 else max(0.0, min(1.0, (1.0 - hhi) / (1.0 - 1.0 / n)))

        # Conservative lower liquidity baseline for real estate
        return QuantSignal(
            total_value=total,
            asset_weights=weights,
            hhi=hhi,
            diversification_score=diversification,
            liquidity_ratio=0.2,
            asset_class_allocations={"real_estate": 1.0},
        )

    async def run(self, ingestion: IngestionResult) -> QuantSignal:
        baseline = self._baseline(ingestion)
        if baseline.total_value <= 0 or not self.client:
            return baseline

        try:
            llm = self.run_structured(
                input_text=(
                    "Analyze these real estate holdings and return QuantSignal.\n"
                    + json.dumps(
                        {
                            "real_estate": [
                                {
                                    "ticker": h.ticker,
                                    "country": h.country,
                                    "city": h.city,
                                    "value": h.value,
                                    "quantity": h.quantity,
                                }
                                for h in ingestion.holdings
                                if h.asset_type == "real_estate"
                            ],
                            "baseline": baseline.model_dump(),
                        }
                    )
                ),
                schema=QuantSignal,
            )
            return QuantSignal(
                total_value=llm.total_value or baseline.total_value,
                asset_weights=llm.asset_weights or baseline.asset_weights,
                hhi=llm.hhi or baseline.hhi,
                diversification_score=llm.diversification_score or baseline.diversification_score,
                liquidity_ratio=llm.liquidity_ratio or baseline.liquidity_ratio,
                asset_class_allocations=llm.asset_class_allocations or baseline.asset_class_allocations,
            )
        except Exception as exc:
            logger.warning("[real_estate] LLM failed, fallback baseline used: %s", exc)
            return baseline