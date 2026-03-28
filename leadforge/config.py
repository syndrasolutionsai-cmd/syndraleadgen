from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = "postgresql+asyncpg://leadforge:leadforge@localhost:5432/leadforge"
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str = "dev-secret-key-change-in-production-min-32-chars"
    encryption_key: str = "dev-enc-key-32b-base64-placeholder="
    access_token_expire_minutes: int = 60

    apify_api_token: str = ""
    hunter_api_key: str = ""
    clearbit_api_key: str = ""
    zerobounce_api_key: str = ""
    serpapi_key: str = ""
    anthropic_api_key: str = ""


settings = Settings()
