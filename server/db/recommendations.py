import logging

logger = logging.getLogger(__name__)


class RecommendationsDB:
    def __init__(self, db):
        self.db = db

    def insert_recommendation(self, run_id, health_score, risk_level, allocation, recs, reasoning):
        data = {
            "analysis_run_id": run_id,
            "portfolio_health_score": health_score,
            "risk_level": risk_level,
            "recommended_allocation": allocation,
            "recommendations": recs,
            "reasoning": reasoning,
        }
        return self.db.table("recommendations").insert(data).execute().data

    def get_recommendation_by_run(self, run_id):
        rows = (
            self.db.table("recommendations")
            .select("*")
            .eq("analysis_run_id", run_id)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
            .data
        )
        return rows[0] if rows else None

    def get_latest_by_user(self, user_id):
        # Uses join through analysis_runs via Supabase embedded select
        rows = (
            self.db.table("recommendations")
            .select("*, analysis_runs!inner(user_id, created_at)")
            .eq("analysis_runs.user_id", user_id)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
            .data
        )
        return rows[0] if rows else None

