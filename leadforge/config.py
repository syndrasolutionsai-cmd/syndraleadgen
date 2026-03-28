import warnings
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEV_SECRET = "dev-secret-key-change-in-production-min-32-chars"
DEV_ENC_KEY = "dev-enc-key-32b-base64-placeholder="


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = "postgresql+asyncpg://leadforge:leadforge@localhost:5432/leadforge"
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str = DEV_SECRET
    encryption_key: str = DEV_ENC_KEY
    access_token_expire_minutes: int = 60

    apify_api_token: str = ""
    hunter_api_key: str = ""
    clearbit_api_key: str = ""
    zerobounce_api_key: str = ""
    serpapi_key: str = ""
    anthropic_api_key: str = ""

    @model_validator(mode="after")
    def warn_dev_secrets(self) -> "Settings":
        if self.secret_key == DEV_SECRET or self.encryption_key == DEV_ENC_KEY:
            warnings.warn(
                "Using development default secrets. Set SECRET_KEY and ENCRYPTION_KEY in .env before deploying.",
                UserWarning,
                stacklevel=2,
            )
        return self


settings = Settings()
