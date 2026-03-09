import json
import os
from dotenv import load_dotenv
from pydantic import SecretStr
from functools import lru_cache

load_dotenv()

class Config:
    GEMINI_API: SecretStr = SecretStr(os.getenv("GEMINI_API_KEY", ""))
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")


    # ── Supabase ──────────────────────────────────────────────────────────────
    SUPABASE_URL: SecretStr = SecretStr(os.getenv("SUPABASE_URL", ""))
    SUPABASE_ANON_KEY: SecretStr = SecretStr(os.getenv("SUPABASE_ANON_KEY", ""))
    SUPABASE_SERVICE_ROLE_KEY: SecretStr = SecretStr(os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""))

    # ── App ───────────────────────────────────────────────────────────────────
    CORS_ORIGINS: list[str] = json.loads(
        os.getenv("CORS_ORIGINS", '["http://localhost:3000"]')
    )

    PIPELINE_INTERVAL_MINUTES: int = int(os.getenv("PIPELINE_INTERVAL_MINUTES", "60"))

    @classmethod
    def validate_config(cls) -> None:
        required_secrets = {
            "SUPABASE_URL": cls.SUPABASE_URL.get_secret_value(),
            "SUPABASE_ANON_KEY": cls.SUPABASE_ANON_KEY.get_secret_value(),
            "SUPABASE_SERVICE_ROLE_KEY": cls.SUPABASE_SERVICE_ROLE_KEY.get_secret_value(),
            "GEMINI_API_KEY": cls.GEMINI_API.get_secret_value(),
            "GEMINI_MODEL": cls.GEMINI_MODEL,
            "CORS_ORIGINS": cls.CORS_ORIGINS,
            "PIPELINE_INTERVAL_MINUTES": cls.PIPELINE_INTERVAL_MINUTES,
        }
        missing_secrets = [
            var_name
            for var_name, var_value in required_secrets.items()
            if not var_value or var_value == "<secret_here>"
        ]
        if missing_secrets:
            raise ValueError(
                f"Missing required secret environment variables: {', '.join(missing_secrets)}. "
                f"Please check your .env file."
            )

    @classmethod
    def get_gemini_api_key(cls) -> str:
        return cls.GEMINI_API.get_secret_value()
    
    @classmethod
    def get_gemini_model(cls) -> str:
        return cls.GEMINI_MODEL

    @classmethod
    def get_supabase_url(cls) -> str:
        return cls.SUPABASE_URL.get_secret_value()

    @classmethod
    def get_supabase_anon_key(cls) -> str:
        return cls.SUPABASE_ANON_KEY.get_secret_value()

    @classmethod
    def get_supabase_service_role_key(cls) -> str:
        return cls.SUPABASE_SERVICE_ROLE_KEY.get_secret_value()

    @classmethod
    def get_cors_origins(cls) -> list[str]:
        return cls.CORS_ORIGINS

    @classmethod
    def get_pipeline_interval_minutes(cls) -> int:
        return cls.PIPELINE_INTERVAL_MINUTES


@lru_cache(maxsize=1)
def getConfig() -> Config:
    config = Config()
    config.validate_config()
    return config
