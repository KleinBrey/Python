"""应用配置管理模块。

使用 Pydantic Settings 管理应用程序的所有配置参数，包括数据库连接、API 密钥、
调度器设置等。支持从 .env 文件加载环境变量。
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


# 项目根目录：从当前文件所在目录往上三级
PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """应用配置类。
    
    所有配置参数都可以通过环境变量覆盖。从项目根目录下的 backend/.env 文件加载配置。
    """
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / "backend" / ".env",
        env_file_encoding="utf-8",
        extra="ignore",  # 忽略 .env 文件中的多余变量
    )

    # ===== 应用基础配置 =====
    app_name: str = "A 股本地行情数据平台"  # 应用名称
    api_prefix: str = "/api"  # API 路由前缀
    database_path: Path = Field(default=PROJECT_ROOT / "data" / "market.duckdb")  # DuckDB 数据库路径
    cors_origins: str = "http://127.0.0.1:5173,http://localhost:5173"  # CORS 允许的源（逗号分隔）

    # ===== HiThink 同花顺 API 配置 =====
    hithink_finance_api_key: str = ""  # 同花顺 API 密钥
    hithink_finance_base_url: str = "https://fuyao.aicubes.cn"  # 同花顺 API 基础 URL
    hithink_timeout_seconds: int = 30  # 同花顺 API 请求超时时间（秒）
    hithink_request_interval: float = 0.0  # 同花顺 API 请求间隔（秒）

    # ===== 定时任务调度配置 =====
    scheduler_enabled: bool = True  # 是否启用定时任务调度器
    scheduler_timezone: str = "Asia/Shanghai"  # 调度器时区
    daily_update_hour: int = 18  # 每日更新任务的执行时间（小时）
    daily_update_minute: int = 0  # 每日更新任务的执行时间（分钟）
    
    # ===== 数据同步配置 =====
    sync_workers: int = 4  # 数据同步的并发工作进程数
    history_days: int = 370  # 获取历史数据的天数

    @field_validator("database_path", mode="after")
    @classmethod
    def resolve_database_path(cls, value: Path) -> Path:
        """验证和转换数据库路径。
        
        如果数据库路径是相对路径，则转换为相对于项目根目录的绝对路径。
        
        Args:
            value: 输入的数据库路径
            
        Returns:
            绝对路径
        """
        return value if value.is_absolute() else PROJECT_ROOT / value

    @property
    def cors_origin_list(self) -> list[str]:
        """将 CORS 源字符串转换为列表。
        
        Returns:
            CORS 源列表，已去除空格和空字符串
        """
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """获取应用配置单例。
    
    使用 LRU 缓存确保在整个应用生命周期中只创建一个 Settings 实例。
    这样可以提高性能，避免重复解析 .env 文件。
    
    Returns:
        全局唯一的 Settings 实例
    """
    return Settings()

