import json
import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import SecretStr

load_dotenv()

class Config:
    APP_ENV: str = os.getenv("APP_ENV", "dev")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    GEMINI_API: SecretStr = SecretStr(os.getenv("GEMINI_API_KEY", ""))
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
    GEMINI_TEMPERATURE: float = float(os.getenv("GEMINI_TEMPERATURE", "0.3"))

    PROMPT_PATH: str = os.getenv(
        "PROMPT_PATH",
        str(Path(__file__).resolve().parents[1] / "agents" / "prompts" / "prompts.yaml"),
    )


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
    def validate_config(cls, required: list[str] | None = None) -> None:
        required_secrets = {
            "SUPABASE_URL": cls.SUPABASE_URL.get_secret_value(),
            "SUPABASE_ANON_KEY": cls.SUPABASE_ANON_KEY.get_secret_value(),
            "SUPABASE_SERVICE_ROLE_KEY": cls.SUPABASE_SERVICE_ROLE_KEY.get_secret_value(),
            "GEMINI_API_KEY": cls.GEMINI_API.get_secret_value(),
            "GEMINI_MODEL": cls.GEMINI_MODEL,
            "CORS_ORIGINS": cls.CORS_ORIGINS,
            "PIPELINE_INTERVAL_MINUTES": cls.PIPELINE_INTERVAL_MINUTES,
            "PROMPT_PATH": cls.PROMPT_PATH,
        }

        if required:
            required_secrets = {k: v for k, v in required_secrets.items() if k in required}

        missing_secrets = [
            var_name
            for var_name, var_value in required_secrets.items()
            if not var_value or var_value == "<secret_here>"
        ]
        if missing_secrets:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_secrets)}. "
                f"Please check your .env file."
            )

    @classmethod
    def get_gemini_api_key(cls) -> str:
        return cls.GEMINI_API.get_secret_value()
    
    @classmethod
    def get_gemini_model(cls) -> str:
        return cls.GEMINI_MODEL

    @classmethod
    def get_gemini_temperature(cls) -> float:
        return cls.GEMINI_TEMPERATURE

    @classmethod
    def get_prompt_path(cls) -> str:
        return cls.PROMPT_PATH

    @classmethod
    def get_app_env(cls) -> str:
        return cls.APP_ENV

    @classmethod
    def get_log_level(cls) -> str:
        return cls.LOG_LEVEL

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
def getConfig(validate: bool = True, required: list[str] | None = None) -> Config:
    config = Config()
    if validate:
        config.validate_config(required=required)
    return config
