from contextlib import contextmanager
from pathlib import Path
from threading import RLock

import duckdb

# 项目根目录：从当前文件所在目录往上三级
PROJECT_ROOT = Path(__file__).resolve().parents[3]

database_path: Path = PROJECT_ROOT / "data" / "simple.duckdb"

schema_path = Path(__file__).parent / "schema.sql"


class DuckDBDatabase:

    # def __init__(self, database_path: str | Path, schema_path: str | Path):
    #     # 把数据库路径转换成完整的绝对路径。
    #     self.database_path = Path(database_path).expanduser().resolve()
    #     self.schema_path = schema_path

    def __init__(self):
        # 把数据库路径转换成完整的绝对路径。
        self.database_path = Path(database_path).expanduser().resolve()
        self.schema_path = schema_path

    # 初始化duckdb
    def initialize(self) -> None:

        # 如果数据库所在的文件夹不存在，就自动创建它。
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

        # 获取初始化SQL脚本
        schema_sql = self.schema_path.read_text(encoding="utf-8")

        # 连接数据库，并执行建表 SQL
        with self.connection() as connection:
            connection.execute(schema_sql)
            print("with 里执行SQL初始化")

    # @contextmanager 让这个生成器函数可以配合 with 使用。
    @contextmanager
    def connection(self, *, read_only: bool = False):
        # 创建duckdb的连接
        connection = duckdb.connect(
            str(self.database_path),
            read_only=read_only,
        )
        print("创建connection")

        try:
            # 把连接交给 with 代码块使用。
            yield connection
        finally:
            # 无论代码是否报错，离开 with 代码块时都会关闭连接。
            connection.close()
            print("关闭connection")
