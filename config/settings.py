from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_env: str = "development"
    secret_key: str = "change-me"
    database_url: str = "******localhost:5432/cfpb_insights"
    redis_url: str = "redis://localhost:6379/0"
    cfpb_api_base: str = "https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/"
    cfpb_lookback_months: int = 6
    access_token_expire_minutes: int = 480

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
