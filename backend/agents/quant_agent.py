import logging
import asyncio
from typing import Any

import numpy as np

from backend.agents.base_agent import BaseAgent
from services.market_data import is_liquid

logger = logging.getLogger(__name__)


class QuantAgent(BaseAgent):

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

        return float(np.clip(norm, 0.0, 1.0))

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:

        holdings = state.get("holdings", [])
        prices = state.get("prices", {})

        if not holdings:
            logger.warning("No holdings found")

            return {
                **state,
                "total_value": 0,
                "asset_weights": {},
                "diversification_score": 0,
                "liquidity_ratio": 0,
            }

        values = {}

        for h in holdings:

            ticker = h["ticker"]

            price = prices.get(ticker)

            if price is None:
                continue

            values[ticker] = h["quantity"] * price

        total_value = sum(values.values())

        if total_value == 0:
            return {
                **state,
                "total_value": 0,
                "asset_weights": {},
                "diversification_score": 0,
                "liquidity_ratio": 0,
            }

        asset_weights = {
            ticker: value / total_value for ticker, value in values.items()
        }

        hhi = self._compute_hhi(asset_weights)

        diversification_score = self._normalise_hhi(hhi, len(asset_weights))

        liquidity_checks = await asyncio.gather(
            *[is_liquid(t) for t in values.keys()]
        )

        liquidity_ratio = sum(liquidity_checks) / len(liquidity_checks)

        return {
            **state,
            "total_value": total_value,
            "asset_weights": asset_weights,
            "hhi": hhi,
            "diversification_score": diversification_score,
            "liquidity_ratio": liquidity_ratio,
        }


_quant_agent = QuantAgent()


async def quant_agent(state: dict[str, Any]):
    return await _quant_agent.run(state)