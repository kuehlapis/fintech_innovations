# controllers/portfolio_controller.py
from fastapi import APIRouter, Depends, HTTPException

from db.assets import AssetsDB
from db.portfolio import PortfolioDB
from db.supabase_client import SupabaseClient
from models.schemas import AssetCreateRequest, AssetUpdateRequest
from services.analysis_service import AnalysisService
from utils.auth import get_current_user, require_user_match

router = APIRouter(prefix="/portfolio", tags=["portfolio"])

db = SupabaseClient().get_client()
assets_db = AssetsDB(db)
portfolio_db = PortfolioDB(db)
analysis_service = AnalysisService()


@router.get("/{user_id}")
def get_portfolio(user_id: str, current_user: dict = Depends(get_current_user)):
    require_user_match(user_id, current_user)
    portfolio = portfolio_db.get_or_create_single_portfolio(user_id)
    assets = assets_db.get_assets(portfolio["id"])
    return {"portfolio": portfolio, "assets": assets}


@router.post("/assets")
async def create_asset(payload: AssetCreateRequest, current_user: dict = Depends(get_current_user)):
    require_user_match(payload.user_id, current_user)
    portfolio = portfolio_db.get_or_create_single_portfolio(payload.user_id)
    insert = payload.model_dump(exclude={"user_id"})
    insert["portfolio_id"] = portfolio["id"]

    created = assets_db.add_asset(insert)
    analysis = await analysis_service.run_and_persist(payload.user_id)
    return {"asset": created[0], "analysis": analysis}


@router.patch("/assets/{asset_id}")
async def update_asset(asset_id: str, payload: AssetUpdateRequest, current_user: dict = Depends(get_current_user)):
    existing = assets_db.get_asset_by_id(asset_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Asset not found")

    user_rows = db.table("portfolios").select("user_id").eq("id", existing["portfolio_id"]).limit(1).execute().data
    user_id = user_rows[0]["user_id"]
    require_user_match(user_id, current_user)

    updated = assets_db.update_asset(asset_id, payload.model_dump(exclude_none=True))
    analysis = await analysis_service.run_and_persist(user_id)
    return {"asset": updated[0], "analysis": analysis}


@router.delete("/assets/{asset_id}")
async def delete_asset(asset_id: str, current_user: dict = Depends(get_current_user)):
    existing = assets_db.get_asset_by_id(asset_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Asset not found")

    user_rows = db.table("portfolios").select("user_id").eq("id", existing["portfolio_id"]).limit(1).execute().data
    user_id = user_rows[0]["user_id"]
    require_user_match(user_id, current_user)

    deleted = assets_db.delete_asset(asset_id)
    analysis = await analysis_service.run_and_persist(user_id)
    return {"deleted": deleted, "analysis": analysis}