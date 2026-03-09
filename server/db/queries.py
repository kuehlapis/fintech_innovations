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

    def _get_portfolio_id(self, user_id: str) -> str | None:
        res = (
            self.client.table("portfolios")
            .select("id")
            .eq("user_id", user_id)
            .maybe_single()
            .execute()
        )
        if not res.data:
            return None
        return res.data["id"]

    async def get_holdings_by_user(self, user_id: str) -> list[dict]:
        def _query():
            portfolio_id = self._get_portfolio_id(user_id)
            if not portfolio_id:
                return []

            res = (
                self.client.table("portfolio_assets")
                .select("quantity, assets(ticker, asset_class)")
                .eq("portfolio_id", portfolio_id)
                .execute()
            )

            return [
                {
                    "ticker": (row.get("assets") or {}).get("ticker", ""),
                    "asset_class": (row.get("assets") or {}).get("asset_class", "other"),
                    "quantity": float(row.get("quantity", 0)),
                }
                for row in (res.data or [])
            ]

        return await asyncio.to_thread(_query)

    async def upsert_holdings(self, holdings: list[dict]) -> list[dict]:
        def _query():
            results = []
            for item in holdings:
                user_id = item.get("user_id")
                ticker = str(item.get("ticker", "")).strip().upper()
                quantity = float(item.get("quantity", 0))
                asset_class = item.get("asset_class", "other")
                if not user_id or not ticker:
                    continue

                portfolio_id = self._get_portfolio_id(user_id)
                if not portfolio_id:
                    created = (
                        self.client.table("portfolios")
                        .insert({"user_id": user_id})
                        .execute()
                    )
                    if not created.data:
                        continue
                    portfolio_id = created.data[0]["id"]

                asset = (
                    self.client.table("assets")
                    .select("id")
                    .eq("ticker", ticker)
                    .maybe_single()
                    .execute()
                )
                if asset.data:
                    asset_id = asset.data["id"]
                else:
                    created_asset = (
                        self.client.table("assets")
                        .insert({"ticker": ticker, "asset_class": asset_class})
                        .execute()
                    )
                    if not created_asset.data:
                        continue
                    asset_id = created_asset.data[0]["id"]

                existing = (
                    self.client.table("portfolio_assets")
                    .select("id")
                    .eq("portfolio_id", portfolio_id)
                    .eq("asset_id", asset_id)
                    .maybe_single()
                    .execute()
                )
                if existing.data:
                    res = (
                        self.client.table("portfolio_assets")
                        .update({"quantity": quantity})
                        .eq("id", existing.data["id"])
                        .execute()
                    )
                else:
                    res = (
                        self.client.table("portfolio_assets")
                        .insert(
                            {
                                "portfolio_id": portfolio_id,
                                "asset_id": asset_id,
                                "quantity": quantity,
                            }
                        )
                        .execute()
                    )
                results.extend(res.data or [])

            return results

        return await asyncio.to_thread(_query)

    async def get_all_user_ids(self) -> list[str]:
        """Return distinct user_ids that have portfolios (used by scheduler)."""
        def _query():
            res = self.client.table("portfolios").select("user_id").execute()
            return [row["user_id"] for row in (res.data or []) if row.get("user_id")]

        return await asyncio.to_thread(_query)


    async def get_portfolio_health(self, user_id: str) -> dict | None:
        def _query():
            portfolio_id = self._get_portfolio_id(user_id)
            if not portfolio_id:
                return None
            res = (
                self.client.table("portfolio_health")
                .select("*")
                .eq("portfolio_id", portfolio_id)
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
            user_id = data.get("user_id")
            portfolio_id = data.get("portfolio_id")

            if not portfolio_id and user_id:
                portfolio_id = self._get_portfolio_id(user_id)
            if not portfolio_id:
                raise RuntimeError("portfolio_id is required for portfolio_health upsert")

            payload = dict(data)
            payload.pop("user_id", None)
            payload["portfolio_id"] = portfolio_id

            res = (
                self.client.table("portfolio_health")
                .upsert(payload, on_conflict="portfolio_id")
                .execute()
            )
            return res.data[0] if res.data else payload

        return await asyncio.to_thread(_query)
    
    async def test_connection(self) -> bool:
        """Test if we can successfully query the database."""
        try:
            res = self.client.table("portfolios").select("id").limit(1).execute()
            return res.status_code == 200
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False