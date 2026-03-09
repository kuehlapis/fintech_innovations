from __future__ import annotations

import asyncio
from typing import Iterable


class MarketDataService:
    """Placeholder market data service with safe defaults."""

    async def get_current_prices(self, tickers: Iterable[str]) -> dict[str, float]:
        await asyncio.sleep(0)
        return {ticker: 1.0 for ticker in tickers}

    async def fetch_news_headlines(self, tickers: Iterable[str]) -> list[str]:
        await asyncio.sleep(0)
        return [f"No recent news for {ticker}." for ticker in tickers]

    async def is_liquid(self, ticker: str) -> bool:
        await asyncio.sleep(0)
        return True
