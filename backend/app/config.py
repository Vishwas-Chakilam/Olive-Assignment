from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
_PROJECT_ROOT = _BACKEND_ROOT.parent
_DATA_DIR = _BACKEND_ROOT / "data"
_DATA_DIR.mkdir(parents=True, exist_ok=True)
_DEFAULT_SQLITE = f"sqlite+aiosqlite:///{(_DATA_DIR / 'ollive.db').as_posix()}"
# MySQL local default — override in .env with your root password
_DEFAULT_MYSQL = "mysql+aiomysql://root:@localhost:3306/ollive"

_ENV_FILES = [p for p in (_BACKEND_ROOT / ".env", _PROJECT_ROOT / ".env") if p.exists()]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ENV_FILES or ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Set DATABASE_URL in .env — e.g. mysql+aiomysql://root:YOUR_PASSWORD@localhost:3306/ollive
    database_url: str = _DEFAULT_MYSQL
    ingestion_url: str = "http://localhost:8000/logs"
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    google_api_key: str = ""
    default_provider: str = "mock"
    default_model: str = "mock-gpt"
    context_message_limit: int = 10
    preview_chars: int = 100
    log_timeout_seconds: float = 2.0
    jwt_secret: str = "change-me-in-production-use-long-random-string"
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 72


settings = Settings()
