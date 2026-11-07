
from functools import lru_cache

from pydantic import field_validator, model_validator
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

    @field_validator("app_env")
    @classmethod
    def validate_app_env(cls, value: str) -> str:
        value = value.strip().lower()

        if value not in {"development", "testing", "production"}:
            raise ValueError("APP_ENV must be development, testing, or production")

        return value

    @field_validator("ai_provider")
    @classmethod
    def validate_ai_provider(cls, value: str) -> str:
        value = value.strip().lower()

        if value not in {"mock", "vultr"}:
            raise ValueError("AI_PROVIDER must be mock or vultr")

        return value

    @field_validator("jwt_algorithm")
    @classmethod
    def validate_jwt_algorithm(cls, value: str) -> str:
        if value != "HS256":
            raise ValueError("Only HS256 is supported")

        return value

    @field_validator("access_token_expire_minutes")
    @classmethod
    def validate_token_expiry(cls, value: int) -> int:
        if not 1 <= value <= 1440:
            raise ValueError(
                "ACCESS_TOKEN_EXPIRE_MINUTES must be between 1 and 1440"
            )

        return value

    @field_validator("cors_origins")
    @classmethod
    def normalize_cors_origins(cls, value: str) -> str:
        origins = [origin.strip().rstrip("/") for origin in value.split(",")]
        origins = [origin for origin in origins if origin]

        if not origins:
            raise ValueError("At least one CORS origin must be configured")

        return ",".join(origins)

    @model_validator(mode="after")
    def validate_security_configuration(self):
        if self.app_env == "production":
            if len(self.jwt_secret_key.encode("utf-8")) < 32:
                raise ValueError(
                    "Production requires a JWT secret of at least 32 bytes"
                )

            if "*" in self.cors_origins.split(","):
                raise ValueError(
                    "Wildcard CORS origins are not allowed in production"
                )

            if self.ai_provider == "mock":
                raise ValueError(
                    "Mock AI provider is not allowed in production"
                )

        if self.ai_provider == "vultr" and not self.vultr_inference_api_key:
            raise ValueError(
                "VULTR_INFERENCE_API_KEY is required when AI_PROVIDER=vultr"
            )

        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
