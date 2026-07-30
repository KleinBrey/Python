"""根目录统一数据层的运行时路径约定。

业务代码只通过这里解析落盘路径，避免各个数据源自行硬编码目录。
"""

from __future__ import annotations

import os
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_ROOT = PROJECT_ROOT / "data"
DATA_STAGES = ("raw", "processed", "cache", "exports")
_SAFE_NAME = re.compile(r"^[a-z0-9][a-z0-9_-]*$")


def resolve_data_root() -> Path:
    """返回统一数据根目录，可通过 STOCK_DATA_DIR 覆盖。"""

    configured = os.getenv("STOCK_DATA_DIR", "").strip()
    root = Path(configured).expanduser() if configured else DEFAULT_DATA_ROOT
    return root.resolve()


def data_stage_dir(stage: str, *, create: bool = False) -> Path:
    """返回 raw/processed/cache/exports 中的一个阶段目录。"""

    if stage not in DATA_STAGES:
        raise ValueError(f"未知数据阶段: {stage}")
    path = resolve_data_root() / stage
    if create:
        path.mkdir(parents=True, exist_ok=True)
    return path


def source_data_dir(source_id: str, *, stage: str = "raw", create: bool = False) -> Path:
    """返回指定数据源目录，例如 data/raw/iwencai。"""

    normalized = source_id.strip().lower()
    if not _SAFE_NAME.fullmatch(normalized):
        raise ValueError(f"无效数据源标识: {source_id}")
    path = data_stage_dir(stage) / normalized
    if create:
        path.mkdir(parents=True, exist_ok=True)
    return path


def export_data_dir(category: str, *, create: bool = False) -> Path:
    """返回导出目录，例如 data/exports/charts。"""

    return source_data_dir(category, stage="exports", create=create)
