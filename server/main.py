from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from agents.schemas import FinalAgentDecision, IngestionRequest
from db.supabase_client import SupabaseClient
from db.queries import Queries
from services.agent_service import AgentService

app = FastAPI()
queries = Queries()
supabase = SupabaseClient()
client = supabase.get_client()
agent_service = AgentService()

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


# Test database connection
@app.get("/test-db")
async def test_db():
    try:
        if await queries.test_connection():
            return {"status": "Database connection successful"}
        raise HTTPException(status_code=500, detail="Database connection failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Create user account
@app.post("/signup")
def signup(email: str, password: str):

    try:
        res = supabase.sign_up(email, password)
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Login
@app.post("/login")
def login(email: str, password: str):

    try:
        res = supabase.log_in(email, password)
        return res
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


# Insert holding
@app.post("/add-holding")
def add_holding(user_id: str, ticker: str, quantity: float):

    try:
        res = client.table("holdings").insert({
            "user_id": user_id,
            "ticker": ticker,
            "quantity": quantity
        }).execute()

        return res.data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Get user holdings
@app.get("/holdings/{user_id}")
def get_holdings(user_id: str):

    res = client.table("holdings") \
        .select("*") \
        .eq("user_id", user_id) \
        .execute()

    return res.data


@app.post("/analyze", response_model=FinalAgentDecision)
async def analyze(request: IngestionRequest):
    try:
        return await agent_service.run_portfolio_analysis(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))