from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ProofRun"
    app_env: str = "development"
    ai_provider: str = "mock"
    database_url: str = "sqlite:///./proofrun.db"

    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    vultr_inference_api_key: str = ""
    vultr_base_url: str = "https://api.vultrinference.com/v1"
    vultr_model: str = "deepseek-v4.1-flash-1017"

    cors_origins: str = "http://localhost:3000,http://127.0.0.1:5500"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
