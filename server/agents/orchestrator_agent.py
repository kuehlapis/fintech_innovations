import uuid
from collections import defaultdict

from agents.guardrail_agent import GuardrailAgent
from agents.registry import AgentRegistry
from models.schemas import FinalAgentDecision, IngestionRequest, QuantSignal


class OrchestratorAgent:
    def __init__(self, registry: AgentRegistry | None = None):
        self.registry = registry or AgentRegistry()
        self.ingestion_agent = self.registry.create("ingestion")
        self.equity_agent = self.registry.create("equity")
        self.crypto_agent = self.registry.create("crypto")
        self.real_estate_agent = self.registry.create("real_estate")
        self.quant_agent = self.registry.create("quant")
        self.sentiment_agent = self.registry.create("sentiment")
        self.advisory_agent = self.registry.create("advisory")
        self.guardrail_agent = GuardrailAgent()

    @staticmethod
    def _blend(base: QuantSignal, specialists: list[QuantSignal]) -> QuantSignal:
        valid = [s for s in specialists if s and s.total_value > 0]
        if not valid:
            return base

        # keep base total/weights for global consistency, blend quality metrics conservatively
        div_scores = [base.diversification_score] + [s.diversification_score for s in valid]
        liq_scores = [base.liquidity_ratio] + [s.liquidity_ratio for s in valid]

        return QuantSignal(
            total_value=base.total_value,
            asset_weights=base.asset_weights,
            hhi=base.hhi,
            diversification_score=sum(div_scores) / len(div_scores),
            liquidity_ratio=sum(liq_scores) / len(liq_scores),
            asset_class_allocations=base.asset_class_allocations,
        )

    async def run(self, request: IngestionRequest) -> FinalAgentDecision:
        request_id = str(uuid.uuid4())
        warnings: list[str] = []

        ingestion = await self.ingestion_agent.run(request)

        equity = QuantSignal()
        crypto = QuantSignal()
        real_estate = QuantSignal()

        try:
            equity = await self.equity_agent.run(ingestion)
        except Exception as exc:
            warnings.append(f"equity agent failed: {exc}")

        try:
            crypto = await self.crypto_agent.run(ingestion)
        except Exception as exc:
            warnings.append(f"crypto agent failed: {exc}")

        try:
            real_estate = await self.real_estate_agent.run(ingestion)
        except Exception as exc:
            warnings.append(f"real_estate agent failed: {exc}")

        quant_base = await self.quant_agent.run(ingestion)
        quant = self._blend(quant_base, [equity, crypto, real_estate])

        sentiment = await self.sentiment_agent.run(ingestion)
        advisory = await self.advisory_agent.run(ingestion, sentiment, quant)
        guardrail = await self.guardrail_agent.run(advisory, ingestion)
        final_advisory = guardrail.adjusted_recommendation or advisory

        split_value = defaultdict(float)
        for idx, h in enumerate(ingestion.holdings):
            key = h.ticker or f"asset_{idx}"
            v = quant.asset_weights.get(key, 0.0) * quant.total_value
            split_value[h.asset_type] += v

        portfolio_split = {
            k: round((v / quant.total_value) * 100.0, 2) if quant.total_value > 0 else 0.0
            for k, v in split_value.items()
        }

        health_raw = (
            quant.diversification_score * 0.4
            + quant.liquidity_ratio * 0.3
            + ((sentiment.sentiment_score + 1.0) / 2.0) * 0.3
        )
        portfolio_health = round(max(0.0, min(1.0, health_raw)) * 100.0, 2)

        return FinalAgentDecision(
            request_id=request_id,
            ingestion=ingestion,
            sentiment=sentiment,
            quant=quant,
            advisory=final_advisory,
            guardrail=guardrail,
            metadata={
                "partial_failure": len(warnings) > 0,
                "warnings": warnings,
                "specialist_quant": {
                    "equity": equity.model_dump(),
                    "crypto": crypto.model_dump(),
                    "real_estate": real_estate.model_dump(),
                },
            },
            portfolio_split=portfolio_split,
            portfolio_health=portfolio_health,
        )