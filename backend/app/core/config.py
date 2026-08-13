from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / "backend" / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "A 股本地行情数据平台"
    api_prefix: str = "/api"
    database_path: Path = Field(default=PROJECT_ROOT / "data" / "market.duckdb")
    cors_origins: str = "http://127.0.0.1:5173,http://localhost:5173"

    hithink_finance_api_key: str = ""
    hithink_finance_base_url: str = "https://fuyao.aicubes.cn"
    hithink_timeout_seconds: int = 30
    hithink_request_interval: float = 0.0

    scheduler_enabled: bool = True
    scheduler_timezone: str = "Asia/Shanghai"
    daily_update_hour: int = 18
    daily_update_minute: int = 0
    sync_workers: int = 4
    history_days: int = 370

    @field_validator("database_path", mode="after")
    @classmethod
    def resolve_database_path(cls, value: Path) -> Path:
        return value if value.is_absolute() else PROJECT_ROOT / value

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

