import asyncio
import logging

from agents.base_agent import BaseAgent
from agents.schemas import IngestionResult, QuantSignal
from services.market_data import MarketDataService

logger = logging.getLogger(__name__)


class QuantAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(agent_type="quant")
        self.market_data = MarketDataService()

    @staticmethod
    def _compute_hhi(weights: dict[str, float]) -> float:
        if not weights:
            return 1.0
        return float(sum(w**2 for w in weights.values()))

    @staticmethod
    def _normalise_hhi(hhi: float, n: int) -> float:
        if n <= 1:
            return 0.0

        min_hhi = 1.0 / n
        max_hhi = 1.0
        norm = (hhi - max_hhi) / (min_hhi - max_hhi)
        return max(0.0, min(1.0, norm))

    async def run(self, ingestion: IngestionResult) -> QuantSignal:
        if not ingestion.holdings:
            logger.warning("[QuantAgent] No holdings found")
            return QuantSignal()

        values: dict[str, float] = {}
        for holding in ingestion.holdings:
            price = ingestion.prices.get(holding.ticker)
            if price is None:
                continue
            values[holding.ticker] = holding.quantity * price

        total_value = sum(values.values())
        if total_value == 0:
            return QuantSignal()

        asset_weights = {ticker: value / total_value for ticker, value in values.items()}
        hhi = self._compute_hhi(asset_weights)
        diversification_score = self._normalise_hhi(hhi, len(asset_weights))

        liquidity_checks = await asyncio.gather(
            *[self.market_data.is_liquid(t) for t in values.keys()]
        )
        liquidity_ratio = sum(liquidity_checks) / max(1, len(liquidity_checks))

        return QuantSignal(
            total_value=total_value,
            asset_weights=asset_weights,
            hhi=hhi,
            diversification_score=diversification_score,
            liquidity_ratio=liquidity_ratio,
        )