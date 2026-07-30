"""兼容入口；新代码请使用 data.paths。"""

from data.paths import (
    DATA_STAGES,
    DEFAULT_DATA_ROOT,
    PROJECT_ROOT,
    data_stage_dir,
    export_data_dir,
    resolve_data_root,
    source_data_dir,
)

__all__ = [
    "DATA_STAGES",
    "DEFAULT_DATA_ROOT",
    "PROJECT_ROOT",
    "data_stage_dir",
    "export_data_dir",
    "resolve_data_root",
    "source_data_dir",
]
