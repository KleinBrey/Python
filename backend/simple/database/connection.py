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

    def initialize(self) -> None:

        # 如果数据库所在的文件夹不存在，就自动创建它。
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

        schema_sql = self.schema_path.read_text(encoding="utf-8")

        # 连接数据库，并执行建表 SQL。
        with self.connection() as connection:
            connection.execute(schema_sql)

    # 函数中使用了 yield，所以它是一个生成器函数。
    # @contextmanager 让这个生成器函数可以配合 with 使用。
    @contextmanager
    def connection(self, *, read_only: bool = False):
        """打开数据库连接，用完后自动关闭。"""

        # read_only=True 表示只读，不允许修改数据库。
        database_connection = duckdb.connect(
            str(self.database_path),
            read_only=read_only,
        )

        try:
            # 把连接交给 with 代码块使用。
            yield database_connection
        finally:
            # 无论代码是否报错，离开 with 代码块时都会关闭连接。
            database_connection.close()
