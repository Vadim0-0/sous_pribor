from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

APP_DIR = Path(__file__).resolve().parent
ENV_FILE = APP_DIR.parent.parent / ".env"


class Settings(BaseSettings):
  model_config = SettingsConfigDict(
    env_file=ENV_FILE,
    env_file_encoding="utf-8",
    extra="ignore",
    case_sensitive=False,
  )

  product_data_url: str

  ai_enabled: bool = True
  ai_base_url: str = "http://ollama:11434"
  ai_model: str = "qwen2.5:3b"
  ai_timeout_seconds: float = 180.0

  feed_cache_ttl_seconds: int = 600


@lru_cache
def get_settings() -> Settings:
  return Settings()


settings = get_settings()