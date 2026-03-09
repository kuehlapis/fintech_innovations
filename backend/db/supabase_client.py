from functools import lru_cache
from supabase import create_client, Client
from utils.config import getConfig


class SupabaseClient:

    def __init__(self):
        self.client = self._create_client()

    @lru_cache(maxsize=1)
    def _create_client(self) -> Client:
        """Return cached Supabase client using service role key."""
        cfg = getConfig()

        url = cfg.get_supabase_url()
        key = cfg.get_supabase_service_role_key()

        if not url or not key:
            raise RuntimeError("Supabase configuration missing")

        return create_client(url, key)

    def get_client(self) -> Client:
        return self.client
    
    def sign_up(self, email: str, password: str) -> dict:
        """Create a new user account with email and password."""
        try:
            res = self.client.auth.sign_up({
                "email": email,
                "password": password
            })
            return res
        except Exception as e:
            raise RuntimeError(f"Sign up failed: {e}")
        
    def log_in(self, email: str, password: str) -> dict:
        """Log in an existing user with email and password."""
        try:
            res = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            return res
        except Exception as e:
            raise RuntimeError(f"Login failed: {e}")
        
    