import logging

from agents.base_agent import BaseAgent
from agents.schemas import IngestionResult, SentimentResult

logger = logging.getLogger(__name__)


class SentimentAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(agent_type="sentiment")

    @staticmethod
    def _score_with_heuristics(headlines: list[str]) -> float:
        if not headlines:
            return 0.0
        positive = {"beat", "upgrade", "growth", "gain", "record", "surge"}
        negative = {"miss", "downgrade", "decline", "loss", "lawsuit", "crash"}

        score = 0
        for headline in headlines:
            words = set(headline.lower().split())
            score += len(words & positive)
            score -= len(words & negative)

        return max(-1.0, min(1.0, score / 10.0))

    def _score_with_llm(self, headlines: list[str]) -> float:
        headlines_text = "\n".join(headlines[:30])
        prompt = (
            "Return a number between -1 and 1 representing market sentiment.\n\n"
            f"Headlines:\n{headlines_text}\n\n"
            "Only return the number."
        )

        raw = self.run_text(prompt)
        try:
            score = float(raw.strip())
            return max(-1.0, min(1.0, score))
        except Exception:
            return self._score_with_heuristics(headlines)

    async def run(self, ingestion: IngestionResult) -> SentimentResult:
        if not ingestion.tickers:
            return SentimentResult(sentiment_score=0.0, news_headlines=[])

        headlines = ingestion.news_headlines
        sentiment_score = self._score_with_llm(headlines)

        return SentimentResult(
            sentiment_score=sentiment_score,
            news_headlines=headlines,
        )