from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    DATABASE_URL: str = "sqlite:///./travel_planner.db"

    ARTIC_BASE_URL: str = "https://api.artic.edu/api/v1"
    ARTIC_CACHE_TTL: int = 300  # seconds
    ARTIC_CACHE_MAX_SIZE: int = 512

    API_PREFIX: str = "/api/v1"

    AUTH_USERNAME: str = "admin"
    AUTH_PASSWORD: str = "secret"


settings = Settings()
