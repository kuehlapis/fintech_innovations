# controllers/portfolio_controller.py
from fastapi import APIRouter, Depends
from agents.orchestrator_agent import OrchestratorAgent
from models.schemas import IngestionRequest, FinalAgentDecision
from db.portfolio import PortfolioDB
from db.supabase_client import SupabaseClient
from services.analysis_service import AnalysisService
from utils.auth import get_current_user, require_user_match

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

db = SupabaseClient().get_client()
portfolio_db = PortfolioDB(db)
analysis_service = AnalysisService()


@router.get("/{user_id}")
def get_dashboard(user_id: str, current_user: dict = Depends(get_current_user)):
    require_user_match(user_id, current_user)

    portfolio = portfolio_db.get_or_create_single_portfolio(user_id)
    assets = (
        db.table("portfolio_assets")
        .select("*")
        .eq("portfolio_id", portfolio["id"])
        .execute()
        .data
    )
    metrics = portfolio_db.get_portfolio_health(user_id)
    latest = analysis_service.get_latest(user_id)

    if not assets and not latest:
        return {
            "empty_state": True,
            "cta": ["add_asset", "add_transaction", "run_analysis"],
            "portfolio": portfolio,
            "metrics": None,
            "latest": None,
        }

    return {
        "empty_state": False,
        "portfolio": portfolio,
        "metrics": metrics,
        "latest": latest,
    }