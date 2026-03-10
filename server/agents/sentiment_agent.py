import json
import logging

from agents.base_agent import BaseAgent
from models.schemas import IngestionResult, SentimentResult
from services.market_data import MarketDataService

logger = logging.getLogger(__name__)


class SentimentAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(agent_type="sentiment")
        self.market_data = MarketDataService()

    async def run(self, ingestion: IngestionResult) -> SentimentResult:
        headlines = list(ingestion.news_headlines or [])
        sector_scores: dict[str, float] = {}

        sectors = sorted(set(h.sector for h in ingestion.holdings if h.sector))
        for sector in sectors:
            sector_tickers = [h.ticker for h in ingestion.holdings if h.sector == sector and h.ticker]
            fetched = await self.market_data.fetch_news_headlines(sector_tickers)
            headlines.extend([h for h in fetched if h])

        baseline = SentimentResult(
            sentiment_score=0.0,
            sector_sentiment={s: 0.0 for s in sectors},
            news_headlines=headlines,
        )

        if not self.client:
            return baseline

        try:
            llm = self.run_structured(
                input_text=(
                    "Analyze sentiment from these sector-tagged headlines. "
                    "Return sector_sentiment in [-1,1] and overall sentiment_score.\n"
                    + json.dumps(
                        {
                            "sectors": sectors,
                            "headlines": headlines,
                            "tickers": ingestion.tickers,
                        }
                    )
                ),
                schema=SentimentResult,
            )

            return SentimentResult(
                sentiment_score=llm.sentiment_score,
                sector_sentiment=llm.sector_sentiment or baseline.sector_sentiment,
                news_headlines=headlines,
            )
        except Exception as exc:
            logger.warning("[sentiment] LLM scoring failed, using baseline: %s", exc)
            return baseline