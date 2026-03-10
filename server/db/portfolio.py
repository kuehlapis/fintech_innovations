import logging

logger = logging.getLogger(__name__)


class PortfolioDB:
    def __init__(self, db):
        self.db = db

    def create_portfolio(self, user_id, name="Primary Portfolio"):
        data = {"user_id": user_id, "portfolio_name": name}
        return self.db.table("portfolios").insert(data).execute().data

    def get_portfolios(self, user_id):
        return self.db.table("portfolios").select("*").eq("user_id", user_id).execute().data

    def get_or_create_single_portfolio(self, user_id):
        rows = self.get_portfolios(user_id)
        if rows:
            return rows[0]
        created = self.create_portfolio(user_id, "Primary Portfolio")
        return created[0]

    def get_portfolio_health(self, user_id):
        rows = (
            self.db.table("portfolio_metrics")
            .select("*")
            .eq("user_id", user_id)
            .order("updated_at", desc=True)
            .limit(1)
            .execute()
            .data
        )
        return rows[0] if rows else None

    def upsert_portfolio_metrics(self, payload):
        return self.db.table("portfolio_metrics").upsert(payload).execute().data