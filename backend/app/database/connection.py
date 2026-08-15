from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from threading import RLock
from typing import Generator

import duckdb


class DuckDBDatabase:
    """DuckDB 短连接管理；进程内写操作串行化。"""

    def __init__(self, path: str | Path):
        self.path = Path(path).expanduser().resolve()
        self._write_lock = RLock()

    def initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        schema = Path(__file__).with_name("schema.sql").read_text(encoding="utf-8")
        with self.write_connection() as connection:
            connection.execute(schema)

    @contextmanager
    def connection(
        self, *, read_only: bool = False
    ) -> Generator[duckdb.DuckDBPyConnection, None, None]:
        connection = duckdb.connect(str(self.path), read_only=read_only)
        try:
            yield connection
        finally:
            connection.close()

    @contextmanager
    def write_connection(self) -> Generator[duckdb.DuckDBPyConnection, None, None]:
        with self._write_lock:
            with self.connection() as connection:
                yield connection
