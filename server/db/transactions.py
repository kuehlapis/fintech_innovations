import logging

logger = logging.getLogger(__name__)


class TransactionsDB:
    def __init__(self, db):
        self.db = db

    def insert_transaction(self, payload: dict):
        return self.db.table("transactions").insert(payload).execute().data

    def get_transactions(self, account_id):
        return (
            self.db.table("transactions")
            .select("*")
            .eq("account_id", account_id)
            .order("transaction_date", desc=True)
            .execute()
            .data
        )

    def update_transaction(self, transaction_id, updates: dict):
        return (
            self.db.table("transactions")
            .update(updates)
            .eq("id", transaction_id)
            .execute()
            .data
        )

    def delete_transaction(self, transaction_id):
        return self.db.table("transactions").delete().eq("id", transaction_id).execute().data