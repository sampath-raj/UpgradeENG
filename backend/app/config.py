from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path

# Look for .env in: backend dir, then project root (one level up)
_HERE = Path(__file__).resolve().parent.parent  # backend/
_ROOT_ENV = _HERE.parent / ".env"              # project root .env
_LOCAL_ENV = _HERE / ".env"                    # backend/.env
_ENV_FILE = str(_LOCAL_ENV) if _LOCAL_ENV.exists() else str(_ROOT_ENV)


class Settings(BaseSettings):
    # App
    app_name: str = "SpeakReady"
    environment: str = "development"
    debug: bool = True

    # Security
    secret_key: str = "change_me_in_production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    # Database — defaults to local SQLite for dev; override with PostgreSQL URL in .env for production
    database_url: str = "sqlite+aiosqlite:///./speakready.db"

    # Anthropic
    anthropic_api_key: str = ""

    # CORS
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    class Config:
        env_file = _ENV_FILE
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
