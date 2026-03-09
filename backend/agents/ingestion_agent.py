"""Agent 1 - normalize incoming portfolio input and enrich with prices."""
import logging

from agents.base_agent import BaseAgent
from agents.schemas import Holding, IngestionRequest, IngestionResult
from db.queries import Queries
from services.market_data import MarketDataService

logger = logging.getLogger(__name__)


class IngestionAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(agent_type="ingestion")
        self.queries = Queries()
        self.market_data = MarketDataService()

    async def _load_holdings(self, request: IngestionRequest) -> list[Holding]:
        if request.holdings:
            return request.holdings

        if not request.user_id:
            return []

        logger.info("[IngestionAgent] Fetching holdings for user %s", request.user_id)
        raw_holdings = await self.queries.get_holdings_by_user(request.user_id)
        return [
            Holding(
                ticker=h.get("ticker", ""),
                quantity=float(h.get("quantity", 0)),
                asset_class=h.get("asset_class", "other"),
            )
            for h in raw_holdings
        ]

    async def run(self, request: IngestionRequest) -> IngestionResult:
        holdings = await self._load_holdings(request)
        tickers = [h.ticker for h in holdings if h.ticker]
        prices = await self.market_data.get_current_prices(tickers)
        news = request.news_headlines or await self.market_data.fetch_news_headlines(
            tickers
        )

        if not holdings:
            logger.warning("[IngestionAgent] No holdings provided")

        return IngestionResult(
            user_id=request.user_id,
            normalized_text=request.raw_text.strip(),
            holdings=holdings,
            tickers=tickers,
            prices=prices,
            news_headlines=news,
        )
