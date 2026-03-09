import logging
from typing import Any

from backend.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class SentimentAgent(BaseAgent):

    def __init__(self):
        super().__init__()

    async def _score_with_llm(self, headlines: list[str]) -> float:

        headlines_text = "\n".join(headlines[:30])

        prompt = f"""
Return a number between -1 and 1 representing market sentiment.

Headlines:
{headlines_text}

Only return the number.
"""

        try:

            raw = await self.chat_text(
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0},
            )

            score = float(raw.strip())

            return max(-1.0, min(1.0, score))

        except Exception:
            return 0.0

    async def run(self, state: dict[str, Any]):

        tickers = state.get("tickers", [])

        if not tickers:
            return {**state, "sentiment_score": 0.0}

        headlines = await self.service.fetch_news_headlines(tickers)

        sentiment_score = await self._score_with_llm(headlines)

        return {
            **state,
            "sentiment_score": sentiment_score,
            "news_headlines": headlines,
        }


_sentiment_agent = SentimentAgent()


async def sentiment_agent(state):
    return await _sentiment_agent.run(state)