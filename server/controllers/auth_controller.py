from fastapi import APIRouter, Depends, HTTPException

from db.portfolio import PortfolioDB
from db.supabase_client import SupabaseClient
from models.schemas import AuthRequest
from utils.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

supabase = SupabaseClient()
db = supabase.get_client()
portfolio_db = PortfolioDB(db)


@router.post("/signup")
def signup(payload: AuthRequest):
    try:
        res = supabase.sign_up(payload.email, payload.password)
        user_id = res.user.id if getattr(res, "user", None) else None
        if not user_id:
            raise RuntimeError("Signup succeeded but no user id returned.")
        portfolio = portfolio_db.get_or_create_single_portfolio(user_id)
        return {"user_id": user_id, "portfolio_id": portfolio["id"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
def login(payload: AuthRequest):
    try:
        res = supabase.log_in(payload.email, payload.password)
        user = getattr(res, "user", None)
        session = getattr(res, "session", None)
        if not user or not session:
            raise RuntimeError("Login failed: no session returned")
        return {
            "user_id": user.id,
            "access_token": session.access_token,
            "refresh_token": session.refresh_token,
            "token_type": "bearer",
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/me")
def me(current_user: dict = Depends(get_current_user)):
    return current_user