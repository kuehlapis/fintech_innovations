"""
agents/ingestion_agent.py
Agent 1 - fetch holdings from Supabase and enrich with live prices.
"""
import logging
from typing import Any

from backend.agents.base_agent import BaseAgent
from db.queries import get_holdings_by_user

logger = logging.getLogger(__name__)


class IngestionAgent(BaseAgent):
    def __init__(self):
        super().__init__()

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        user_id: str = state["user_id"]
        logger.info("[IngestionAgent] Fetching holdings for user %s", user_id)

        holdings = await get_holdings_by_user(user_id)
        if not holdings:
            logger.warning("[IngestionAgent] No holdings found for user %s", user_id)
            return {**state, "holdings": [], "prices": {}, "tickers": []}

        tickers = [h["ticker"] for h in holdings]
        prices = await get_current_prices(tickers)

        logger.info(
            "[IngestionAgent] Retrieved %d holdings, %d prices",
            len(holdings),
            len(prices),
        )
        return {**state, "holdings": holdings, "prices": prices, "tickers": tickers}


_ingestion_agent = IngestionAgent()


async def ingestion_agent(state: dict[str, Any]) -> dict[str, Any]:
    return await _ingestion_agent.run(state)
