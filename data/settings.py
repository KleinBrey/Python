"""项目本地配置读取。

真实密钥保存在根目录 ``config/secrets.local.toml``。该文件被 Git 忽略，
模板 ``config/secrets.example.toml`` 可以安全提交。
"""

from __future__ import annotations

from functools import lru_cache
import os
from pathlib import Path
import re
import shlex
import tomllib
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOCAL_SETTINGS_FILE = PROJECT_ROOT / "config" / "secrets.local.toml"


class SettingsError(RuntimeError):
    """项目配置文件缺失或格式错误。"""


@lru_cache(maxsize=1)
def load_local_settings() -> dict[str, str]:
    if not LOCAL_SETTINGS_FILE.is_file():
        return {}
    try:
        payload = tomllib.loads(LOCAL_SETTINGS_FILE.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise SettingsError(f"无法读取本地配置 {LOCAL_SETTINGS_FILE}: {exc}") from exc

    settings = payload.get("settings", {})
    if not isinstance(settings, dict):
        raise SettingsError(
            f"{LOCAL_SETTINGS_FILE} 中的 [settings] 必须是 TOML 表"
        )
    return {
        str(name): str(value).strip()
        for name, value in settings.items()
        if value is not None
    }


def read_profile_value(name: str) -> str:
    """兼容旧配置：只读取 shell profile 中指定变量，不执行 profile。"""

    pattern = re.compile(rf"^\s*(?:export\s+)?{re.escape(name)}\s*=\s*(.*?)\s*$")
    for path in (
        Path.home() / ".zshrc",
        Path.home() / ".zprofile",
        Path.home() / ".profile",
    ):
        if not path.is_file():
            continue
        for line in reversed(
            path.read_text(encoding="utf-8", errors="replace").splitlines()
        ):
            match = pattern.match(line)
            if not match:
                continue
            try:
                parts = shlex.split(match.group(1), posix=True)
            except ValueError as exc:
                raise SettingsError(f"{path} 中 {name} 的引号不完整") from exc
            return parts[0] if parts else ""
    return ""


def get_setting(name: str, default: Any = "") -> str:
    """按项目本地文件、环境变量、shell profile、默认值的顺序读取。"""

    local_value = load_local_settings().get(name, "").strip()
    if local_value:
        return local_value
    environment_value = os.environ.get(name, "").strip()
    if environment_value:
        return environment_value
    profile_value = read_profile_value(name).strip()
    return profile_value or str(default)
