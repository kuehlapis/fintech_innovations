
import logging


logger = logging.getLogger(__name__)
class AccountsDB:
    def __init__(self, db):
        self.db = db
    def create_account(self, user_id, account_type, institution, name):
        try:
            data = {
                "user_id": user_id,
                "account_type": account_type,
                "institution_name": institution,
                "account_name": name
            }
            result = self.db.table("financial_accounts").insert(data).execute()
            print(f"Create account result: {result}")
            return result.data      
        except Exception as e:
            logger.error(f"Error creating account: {e}")
            raise e
        
    def get_accounts(self, user_id):
        try:
            result = self.db.table("financial_accounts")\
                .select("*")\
                .eq("user_id", user_id)\
                .execute()
            print(f"Get accounts result: {result}")
            return result.data
        except Exception as e:
            logger.error(f"Error fetching accounts: {e}")
            raise e
        
    def delete_account(self,account_id):
        try:
            result = self.db.table("financial_accounts")\
                .delete()\
                .eq("id", account_id)\
                .execute()
            print(f"Delete account result: {result}")
            return result.data
        except Exception as e:
            logger.error(f"Error deleting account: {e}")
            raise e