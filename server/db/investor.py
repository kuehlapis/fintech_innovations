
import logging


logger = logging.getLogger(__name__)

class InvestorDB:
    def __init__(self, db):
        self.db = db

    def get_investor_profile(self, user_id):
        try:
            response = self.db.table("investor_profiles")\
                .select("*")\
                .eq("user_id", user_id)\
                .execute()
            result =  response.data
            print(f"Get investor profile result: {result}")
            return result
        except Exception as e:
            logger.error(f"Error fetching investor profile: {e}")
            raise e
    
    def insert_investor_profile(self, user_id, risk, horizon):
        try:
            data = {
                "user_id": user_id,
                "risk_tolerance": risk,
                "investment_horizon": horizon
            }
            result = self.db.table("investor_profiles").insert(data).execute()
            print(f"Insert investor profile result: {result}")
            return result.data
        except Exception as e:
            logger.error(f"Error inserting investor profile: {e}")
            raise e
        
    def update_investor_profile(self, user_id, updates):
        try:
            result = self.db.table("investor_profiles")\
                .update(updates)\
                .eq("user_id", user_id)\
                .execute()
            print(f"Update investor profile result: {result}")
            return result.data
        except Exception as e:
            logger.error(f"Error updating investor profile: {e}")
            raise e
        
    def delete_investor_profile(self, user_id):
        try:
            result = self.db.table("investor_profiles")\
                .delete()\
                .eq("user_id", user_id)\
                .execute()
            print(f"Delete investor profile result: {result}")
            return result.data
        except Exception as e:
            logger.error(f"Error deleting investor profile: {e}")
            raise e