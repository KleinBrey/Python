"""系统结构化数据源目录。"""

from __future__ import annotations

from data.schemas import SourceMetadata


_SOURCES = {
    "hithink-financial": SourceMetadata(
        source_id="hithink-financial",
        name="同花顺扶摇 Financial API",
        kind="官方 REST API",
        credential_env="HITHINK_FINANCE_API_KEY",
        dependency=None,
        capabilities=(
            "ticker_master",
            "snapshot",
            "daily_bars",
            "valuations",
            "financials",
            "hot_rankings",
            "limit_up",
            "funds",
        ),
        description="系统唯一结构化证券数据源；问财仅保留为自然语言选股入口。",
        docs_url="https://fuyao.aicubes.cn/docs/",
    )
}


def get_source(source_id: str) -> SourceMetadata:
    try:
        return _SOURCES[source_id]
    except KeyError as exc:
        raise KeyError(f"未注册的数据源: {source_id}") from exc


def list_sources() -> list[SourceMetadata]:
    return list(_SOURCES.values())
