"""
Central application configuration.

All environment-driven settings (secret keys, database URL, Gemini API key,
token lifetime, etc.) are loaded here via pydantic-settings so the rest of
the codebase never touches os.environ directly.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FinRelief AI"
    secret_key: str = "finrelief-ai-super-secret-key-change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    database_url: str = "sqlite:///./finrelief.db"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
