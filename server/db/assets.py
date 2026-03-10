import logging

logger = logging.getLogger(__name__)


class AssetsDB:
    def __init__(self, db):
        self.db = db

    def add_asset(self, payload: dict):
        return self.db.table("portfolio_assets").insert(payload).execute().data

    def get_assets(self, portfolio_id):
        return (
            self.db.table("portfolio_assets")
            .select("*")
            .eq("portfolio_id", portfolio_id)
            .execute()
            .data
        )

    def get_asset_by_id(self, asset_id):
        rows = (
            self.db.table("portfolio_assets")
            .select("*")
            .eq("id", asset_id)
            .limit(1)
            .execute()
            .data
        )
        return rows[0] if rows else None

    def update_asset(self, asset_id, updates: dict):
        return (
            self.db.table("portfolio_assets")
            .update(updates)
            .eq("id", asset_id)
            .execute()
            .data
        )

    def delete_asset(self, asset_id):
        return self.db.table("portfolio_assets").delete().eq("id", asset_id).execute().data