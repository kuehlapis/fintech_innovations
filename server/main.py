from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agents.schemas import FinalAgentDecision, IngestionRequest
from db.queries import Queries
from db.supabase_client import SupabaseClient
from services.agent_service import AgentService

app = FastAPI()
queries = Queries()
supabase = SupabaseClient()
client = supabase.get_client()
agent_service = AgentService()


class AuthRequest(BaseModel):
    email: str
    password: str


class AddHoldingRequest(BaseModel):
    user_id: str
    ticker: str
    quantity: float
    asset_class: str = "equity"


def _get_or_create_portfolio_id(user_id: str) -> str:
    existing = (
        client.table("portfolios")
        .select("id")
        .eq("user_id", user_id)
        .maybe_single()
        .execute()
    )
    if existing.data:
        return existing.data["id"]

    created = client.table("portfolios").insert({"user_id": user_id}).execute()
    if not created.data:
        raise RuntimeError("Unable to create portfolio")
    return created.data[0]["id"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {"status": "API running"}


@app.get("/test-db")
async def test_db():
    try:
        if await queries.test_connection():
            return {"status": "Database connection successful"}
        raise HTTPException(status_code=500, detail="Database connection failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/signup")
def signup(request: AuthRequest):
    try:
        return supabase.sign_up(request.email, request.password)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/login")
def login(request: AuthRequest):
    try:
        return supabase.log_in(request.email, request.password)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@app.post("/add-holding")
def add_holding(request: AddHoldingRequest):
    try:
        ticker = request.ticker.strip().upper()
        portfolio_id = _get_or_create_portfolio_id(request.user_id)

        asset = (
            client.table("assets")
            .select("id")
            .eq("ticker", ticker)
            .maybe_single()
            .execute()
        )

        if asset.data:
            asset_id = asset.data["id"]
        else:
            created_asset = (
                client.table("assets")
                .insert({"ticker": ticker, "asset_class": request.asset_class})
                .execute()
            )
            if not created_asset.data:
                raise RuntimeError("Unable to create asset")
            asset_id = created_asset.data[0]["id"]

        existing_row = (
            client.table("portfolio_assets")
            .select("id, quantity")
            .eq("portfolio_id", portfolio_id)
            .eq("asset_id", asset_id)
            .maybe_single()
            .execute()
        )

        if existing_row.data:
            new_quantity = float(existing_row.data.get("quantity", 0)) + request.quantity
            res = (
                client.table("portfolio_assets")
                .update({"quantity": new_quantity})
                .eq("id", existing_row.data["id"])
                .execute()
            )
        else:
            res = (
                client.table("portfolio_assets")
                .insert(
                    {
                        "portfolio_id": portfolio_id,
                        "asset_id": asset_id,
                        "quantity": request.quantity,
                    }
                )
                .execute()
            )

        return res.data or []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/holdings/{user_id}")
def get_holdings(user_id: str):
    try:
        portfolio = (
            client.table("portfolios")
            .select("id")
            .eq("user_id", user_id)
            .maybe_single()
            .execute()
        )

        if not portfolio.data:
            return []

        rows = (
            client.table("portfolio_assets")
            .select("quantity, assets(ticker, asset_class)")
            .eq("portfolio_id", portfolio.data["id"])
            .execute()
        )

        return [
            {
                "ticker": (row.get("assets") or {}).get("ticker", ""),
                "asset_class": (row.get("assets") or {}).get("asset_class", "other"),
                "quantity": float(row.get("quantity", 0)),
            }
            for row in (rows.data or [])
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze", response_model=FinalAgentDecision)
async def analyze(request: IngestionRequest):
    try:
        return await agent_service.run_portfolio_analysis(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
