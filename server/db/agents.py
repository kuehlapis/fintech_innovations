import logging

logger = logging.getLogger(__name__)


class AgentsDB:
    def __init__(self, db):
        self.db = db

    def create_analysis_run(self, user_id, portfolio_id, status="pending"):
        data = {"user_id": user_id, "portfolio_id": portfolio_id, "status": status}
        return self.db.table("analysis_runs").insert(data).execute().data

    def update_analysis_run_status(self, run_id, status):
        return (
            self.db.table("analysis_runs")
            .update({"status": status})
            .eq("id", run_id)
            .execute()
            .data
        )

    def get_analysis_runs(self, user_id):
        return (
            self.db.table("analysis_runs")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
            .data
        )

    def get_latest_analysis_run(self, user_id):
        data = (
            self.db.table("analysis_runs")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
            .data
        )
        return data[0] if data else None

    def insert_agent_output(self, run_id, agent_name, output):
        data = {"analysis_run_id": run_id, "agent_name": agent_name, "output": output}
        return self.db.table("agent_outputs").insert(data).execute().data

    def get_agent_outputs(self, run_id):
        return (
            self.db.table("agent_outputs")
            .select("*")
            .eq("analysis_run_id", run_id)
            .order("created_at", desc=False)
            .execute()
            .data
        )
