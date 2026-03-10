# ingestion_agent.py
import json
import logging
from pydantic import BaseModel, Field

from agents.base_agent import BaseAgent
from models.schemas import Holding, IngestionRequest, IngestionResult

logger = logging.getLogger(__name__)


class IngestionLLMOutput(BaseModel):
    normalized_text: str = ""
    holdings: list[Holding] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)


class IngestionAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(agent_type="ingestion")

    async def run(self, request: IngestionRequest) -> IngestionResult:
        holdings = request.holdings or []
        tickers = [h.ticker for h in holdings if h.ticker]
        prices = {t: 100.0 for t in tickers}  # replace with market data service

        # Deterministic baseline
        baseline = IngestionResult(
            user_id=request.user_id,
            normalized_text=request.raw_text or "",
            holdings=holdings,
            tickers=tickers,
            prices=prices,
            news_headlines=request.news_headlines or [],
        )

        # LLM enrichment when available
        if not self.client:
            return baseline

        try:
            prompt_payload = {
                "user_id": request.user_id,
                "raw_text": request.raw_text,
                "holdings": [h.model_dump() for h in holdings],
            }
            llm = self.run_structured(
                input_text=f"Normalize this portfolio input:\n{json.dumps(prompt_payload)}",
                schema=IngestionLLMOutput,
            )

            merged_holdings = llm.holdings if llm.holdings else baseline.holdings
            merged_tickers = [h.ticker for h in merged_holdings if h.ticker]
            merged_prices = {t: prices.get(t, 100.0) for t in merged_tickers}

            return IngestionResult(
                user_id=request.user_id,
                normalized_text=llm.normalized_text or baseline.normalized_text,
                holdings=merged_holdings,
                tickers=merged_tickers,
                prices=merged_prices,
                news_headlines=baseline.news_headlines,
            )
        except Exception as exc:
            logger.warning("[ingestion] LLM enrichment failed, using baseline: %s", exc)
            return baseline