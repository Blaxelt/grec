from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    database_url: str
    steam_api_key: str = ""
    cors_origin: str = "http://localhost:5173"
    cf_model_dir: Path = _PROJECT_ROOT / "data" / "models" / "cf"

    model_config = SettingsConfigDict(env_file=_PROJECT_ROOT / ".env", extra="ignore")

settings = Settings()