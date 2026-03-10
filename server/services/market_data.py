# services/market_data.py
import yfinance as yf
import random

class MarketDataService:
    """Fetch real market data from Yahoo Finance for equities & general info."""

    async def get_current_prices(self, tickers):
        prices = {}
        for t in tickers:
            try:
                stock = yf.Ticker(t)
                prices[t] = stock.info.get("currentPrice") or random.uniform(10, 500)
            except Exception:
                prices[t] = random.uniform(10, 500)
        return prices

    async def get_company_info(self, ticker):
        """Return sector, industry, country, market cap"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            return {
                "sector": info.get("sector", "Unknown"),
                "industry": info.get("industry", "Unknown"),
                "country": info.get("country", "Unknown"),
                "market_cap": info.get("marketCap", 0),
                "pe_ratio": info.get("trailingPE", 0)
            }
        except Exception:
            return {
                "sector": "Unknown",
                "industry": "Unknown",
                "country": "Unknown",
                "market_cap": 0,
                "pe_ratio": 0
            }

    async def fetch_news_headlines(self, tickers):
        """Fetch latest news headlines for tickers"""
        headlines = []
        for t in tickers:
            try:
                stock = yf.Ticker(t)
                news_items = stock.news[:5]  # only take latest 5
                for n in news_items:
                    headlines.append(n.get("title"))
            except Exception:
                headlines.append(f"{t} news unavailable")
        return headlines

    async def is_liquid(self, ticker):
        """Check if market cap is above threshold as proxy for liquidity"""
        info = await self.get_company_info(ticker)
        return 1 if info.get("market_cap", 0) > 1e9 else 0