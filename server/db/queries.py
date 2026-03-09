"""
db/queries.py – async-compatible Supabase query helpers
"""
import asyncio
import logging
from typing import Any

from db.supabase_client import SupabaseClient

logger = logging.getLogger(__name__)


class Queries:
    def __init__(self):
        self.client = SupabaseClient().get_client()

    async def get_holdings_by_user(self, user_id: str) -> list[dict]:
        def _query():
            res = (
                self.client.table("holdings")
                .select("*")
                .eq("user_id", user_id)
                .execute()
            )
            return res.data or []

        return await asyncio.to_thread(_query)

    async def upsert_holdings(self, holdings: list[dict]) -> list[dict]:
        def _query():
            res = (
                self.client.table("holdings")
                .upsert(holdings, on_conflict="user_id,ticker")
                .execute()
            )
            return res.data or []

        return await asyncio.to_thread(_query)

    async def get_all_user_ids(self) -> list[str]:
        """Return distinct user_ids that have holdings (used by scheduler)."""
        def _query():
            res = self.client.table("holdings").select("user_id").execute()
            seen = set()
            ids = []
            for row in res.data or []:
                uid = row["user_id"]
                if uid not in seen:
                    seen.add(uid)
                    ids.append(uid)
            return ids

        return await asyncio.to_thread(_query)


    async def get_portfolio_health(self, user_id: str) -> dict | None:
        def _query():
            res = (
                self.client.table("portfolio_health")
                .select("*")
                .eq("user_id", user_id)
                .single()
                .execute()
            )
            return res.data

        try:
            return await asyncio.to_thread(_query)
        except Exception:
            return None

    async def upsert_portfolio_health(self, data: dict) -> dict:
        def _query():
            res = (
                self.client.table("portfolio_health")
                .upsert(data, on_conflict="user_id")
                .execute()
            )
            return res.data[0] if res.data else data

        return await asyncio.to_thread(_query)
    
    async def test_connection(self) -> bool:
        """Test if we can successfully query the database."""
        try:
            res = self.client.table("holdings").select("*").limit(1).execute()
            return res.status_code == 200
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False