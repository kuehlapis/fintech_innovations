from fastapi import APIRouter, HTTPException

from db.accounts import AccountsDB
from db.supabase_client import SupabaseClient
from db.transactions import TransactionsDB
from models.schemas import (
    AccountCreateRequest,
    TransactionCreateRequest,
    TransactionUpdateRequest,
)
from services.analysis_service import AnalysisService

router = APIRouter(prefix="/transactions", tags=["transactions"])

db = SupabaseClient().get_client()
accounts_db = AccountsDB(db)
tx_db = TransactionsDB(db)
analysis_service = AnalysisService()


@router.post("/accounts")
def create_account(payload: AccountCreateRequest):
    data = {
        "user_id": payload.user_id,
        "account_type": payload.account_type,
        "institution_name": payload.institution_name,
        "account_name": payload.account_name,
        "currency": payload.currency,
    }
    created = db.table("financial_accounts").insert(data).execute().data
    return {"account": created[0]}


@router.get("/accounts/{user_id}")
def get_accounts(user_id: str):
    return {"accounts": accounts_db.get_accounts(user_id)}


@router.post("")
async def create_transaction(payload: TransactionCreateRequest):
    account = (
        db.table("financial_accounts")
        .select("id,user_id")
        .eq("id", payload.account_id)
        .limit(1)
        .execute()
        .data
    )
    if not account:
        raise HTTPException(status_code=400, detail="Account not found")

    created = tx_db.insert_transaction(payload.model_dump())
    user_id = account[0]["user_id"]
    analysis = await analysis_service.run_and_persist(user_id)
    return {"transaction": created[0], "analysis": analysis}


@router.patch("/{transaction_id}")
async def update_transaction(transaction_id: str, payload: TransactionUpdateRequest):
    existing = (
        db.table("transactions")
        .select("id,account_id")
        .eq("id", transaction_id)
        .limit(1)
        .execute()
        .data
    )
    if not existing:
        raise HTTPException(status_code=404, detail="Transaction not found")

    account = (
        db.table("financial_accounts")
        .select("id,user_id")
        .eq("id", existing[0]["account_id"])
        .limit(1)
        .execute()
        .data
    )
    user_id = account[0]["user_id"]

    updated = tx_db.update_transaction(transaction_id, payload.model_dump(exclude_none=True))
    analysis = await analysis_service.run_and_persist(user_id)
    return {"transaction": updated[0], "analysis": analysis}


@router.delete("/{transaction_id}")
async def delete_transaction(transaction_id: str):
    existing = (
        db.table("transactions")
        .select("id,account_id")
        .eq("id", transaction_id)
        .limit(1)
        .execute()
        .data
    )
    if not existing:
        raise HTTPException(status_code=404, detail="Transaction not found")

    account = (
        db.table("financial_accounts")
        .select("id,user_id")
        .eq("id", existing[0]["account_id"])
        .limit(1)
        .execute()
        .data
    )
    user_id = account[0]["user_id"]

    deleted = tx_db.delete_transaction(transaction_id)
    analysis = await analysis_service.run_and_persist(user_id)
    return {"deleted": deleted, "analysis": analysis}