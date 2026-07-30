"""根目录 data 的统一落盘工具。raw 保留原貌，processed 只保存标准格式。"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from data.paths import source_data_dir


def _safe_dataset_name(dataset: str) -> str:
    normalized = dataset.strip().lower().replace(" ", "_")
    if not normalized or any(character not in "abcdefghijklmnopqrstuvwxyz0123456789_-" for character in normalized):
        raise ValueError(f"无效数据集名称: {dataset}")
    return normalized


def write_raw_json(source: str, dataset: str, payload: Any) -> Path:
    directory = source_data_dir(source, stage="raw", create=True)
    path = directory / f"{_safe_dataset_name(dataset)}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return path


def write_processed_csv(source: str, dataset: str, frame: pd.DataFrame) -> Path:
    directory = source_data_dir(source, stage="processed", create=True)
    path = directory / f"{_safe_dataset_name(dataset)}.csv"
    frame.to_csv(path, index=False, encoding="utf-8-sig")
    return path


def write_processed_snapshot(source: str, dataset: str, frame: pd.DataFrame) -> Path:
    directory = source_data_dir(source, stage="processed", create=True) / "history"
    directory.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().astimezone().strftime("%Y%m%d_%H%M%S")
    path = directory / f"{_safe_dataset_name(dataset)}_{timestamp}.csv"
    frame.to_csv(path, index=False, encoding="utf-8-sig")
    return path
