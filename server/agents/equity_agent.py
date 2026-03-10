import json
import logging

from agents.base_agent import BaseAgent
from models.schemas import IngestionResult, QuantSignal
from services.market_data import MarketDataService

logger = logging.getLogger(__name__)


class EquityAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(agent_type="equity")
        self.market_data = MarketDataService()

    async def _enriched_holdings(self, ingestion: IngestionResult):
        equity_holdings = [h for h in ingestion.holdings if h.asset_type == "equity"]
        enriched = []
        for h in equity_holdings:
            info = await self.market_data.get_company_info(h.ticker) if h.ticker else {}
            enriched.append(
                {
                    "ticker": h.ticker,
                    "quantity": h.quantity,
                    "value": h.value,
                    "sector": h.sector or info.get("sector"),
                    "country": h.country or info.get("country"),
                    "market_cap": info.get("market_cap", 0),
                }
            )
        return enriched

    def _baseline(self, enriched: list[dict]) -> QuantSignal:
        if not enriched:
            return QuantSignal()

        total = 0.0
        values = {}
        for idx, row in enumerate(enriched):
            key = row.get("ticker") or f"equity_{idx}"
            v = float(row.get("value") or 0.0)
            if v <= 0:
                v = float(row.get("quantity") or 0.0) * 100.0
            v = max(v, 0.0)
            values[key] = v
            total += v

        if total <= 0:
            return QuantSignal()

        weights = {k: v / total for k, v in values.items()}
        hhi = sum(w * w for w in weights.values())
        n = max(len(weights), 1)
        diversification = 1.0 if n == 1 else max(0.0, min(1.0, (1.0 - hhi) / (1.0 - 1.0 / n)))

        return QuantSignal(
            total_value=total,
            asset_weights=weights,
            hhi=hhi,
            diversification_score=diversification,
            liquidity_ratio=0.85,
            asset_class_allocations={"equity": 1.0},
        )

    async def run(self, ingestion: IngestionResult) -> QuantSignal:
        enriched = await self._enriched_holdings(ingestion)
        baseline = self._baseline(enriched)

        if baseline.total_value <= 0 or not self.client:
            return baseline

        try:
            llm = self.run_structured(
                input_text=(
                    "Analyze these equity holdings and return QuantSignal.\n"
                    + json.dumps({"equities": enriched, "baseline": baseline.model_dump()})
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
            logger.warning("[equity] LLM failed, fallback baseline used: %s", exc)
            return baseline