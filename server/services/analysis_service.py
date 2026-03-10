from __future__ import annotations

from typing import Any, Dict, List

from agents.orchestrator_agent import OrchestratorAgent
from db.agents import AgentsDB
from db.assets import AssetsDB
from db.portfolio import PortfolioDB
from db.recommendations import RecommendationsDB
from db.supabase_client import SupabaseClient
from models.schemas import FinalAgentDecision, Holding, IngestionRequest


class AnalysisService:
    def __init__(self) -> None:
        db = SupabaseClient().get_client()
        self.db = db
        self.portfolio_db = PortfolioDB(db)
        self.assets_db = AssetsDB(db)
        self.agents_db = AgentsDB(db)
        self.recs_db = RecommendationsDB(db)
        self.orchestrator = OrchestratorAgent()

    def _to_holdings(self, assets: List[Dict[str, Any]]) -> List[Holding]:
        result: List[Holding] = []
        for row in assets:
            result.append(
                Holding(
                    ticker=row.get("ticker"),
                    quantity=float(row.get("quantity") or 1.0),
                    asset_type=row.get("asset_type"),
                    sector=row.get("sector"),
                    country=row.get("country"),
                    city=row.get("city"),
                    value=float(row.get("value") or 0.0),
                    asset_name=row.get("asset_name"),
                )
            )
        return result

    def _risk_level(self, hhi: float) -> str:
        if hhi >= 0.25:
            return "high"
        if hhi >= 0.15:
            return "medium"
        return "low"

    async def run_and_persist(self, user_id: str, raw_text: str = "") -> dict:
        portfolio = self.portfolio_db.get_or_create_single_portfolio(user_id)
        portfolio_id = portfolio["id"]

        run = self.agents_db.create_analysis_run(user_id, portfolio_id, status="pending")[0]
        run_id = run["id"]

        try:
            self.agents_db.update_analysis_run_status(run_id, "running")

            assets = self.assets_db.get_assets(portfolio_id)
            holdings = self._to_holdings(assets)

            decision: FinalAgentDecision = await self.orchestrator.run(
                IngestionRequest(user_id=user_id, holdings=holdings, raw_text=raw_text)
            )

            self.agents_db.insert_agent_output(run_id, "ingestion", decision.ingestion.model_dump())
            self.agents_db.insert_agent_output(run_id, "quant", decision.quant.model_dump())
            self.agents_db.insert_agent_output(run_id, "sentiment", decision.sentiment.model_dump())
            self.agents_db.insert_agent_output(run_id, "advisory", decision.advisory.model_dump())
            self.agents_db.insert_agent_output(run_id, "guardrail", decision.guardrail.model_dump())

            self.recs_db.insert_recommendation(
                run_id=run_id,
                health_score=decision.portfolio_health,
                risk_level=self._risk_level(decision.quant.hhi),
                allocation=decision.portfolio_split,
                recs={
                    "summary": decision.advisory.summary,
                    "actions": decision.advisory.actions,
                    "risks": decision.advisory.risks,
                    "warnings": decision.advisory.warnings,
                },
                reasoning=decision.advisory.rationale,
            )

            self.portfolio_db.upsert_portfolio_metrics(
                {
                    "user_id": user_id,
                    "portfolio_id": portfolio_id,
                    "portfolio_health_score": decision.portfolio_health,
                    "crypto_percentage": decision.portfolio_split.get("crypto", 0),
                    "equity_percentage": decision.portfolio_split.get("equity", 0),
                    "real_estate_percentage": decision.portfolio_split.get("real_estate", 0),
                    "savings_percentage": decision.portfolio_split.get("savings", 0),
                    "bond_percentage": decision.portfolio_split.get("bond", 0),
                }
            )

            self.agents_db.update_analysis_run_status(run_id, "completed")
            return {
                "run_id": run_id,
                "status": "completed",
                "result": decision.model_dump(),
            }

        except Exception as exc:
            self.agents_db.update_analysis_run_status(run_id, "failed")
            raise RuntimeError(f"Analysis failed: {exc}") from exc

    def get_history(self, user_id: str):
        return self.agents_db.get_analysis_runs(user_id)

    def get_latest(self, user_id: str):
        run = self.agents_db.get_latest_analysis_run(user_id)
        if not run:
            return None
        outputs = self.agents_db.get_agent_outputs(run["id"])
        rec = self.recs_db.get_recommendation_by_run(run["id"])
        return {"run": run, "outputs": outputs, "recommendation": rec}