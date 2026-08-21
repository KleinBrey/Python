from contextlib import contextmanager
from pathlib import Path
from threading import RLock

import duckdb


class DuckDBDatabase:
    """负责创建、打开和关闭 DuckDB 数据库连接。"""

    def __init__(self, path: str | Path):
        # 把数据库路径转换成完整的绝对路径。
        self.path = Path(path).expanduser().resolve()

        # 使用锁避免多个线程同时写数据库而产生冲突。
        # 获得锁的写操作先执行，其他写操作会等待。
        self._write_lock = RLock()

    def initialize(self) -> None:
        """创建数据库目录，并执行 schema.sql 中的建表语句。"""

        # 如果数据库所在的文件夹不存在，就自动创建它。
        self.path.parent.mkdir(parents=True, exist_ok=True)

        # schema.sql 和当前文件放在同一个文件夹中。
        schema_path = Path(__file__).parent / "schema.sql"
        schema_sql = schema_path.read_text(encoding="utf-8")

        # 连接数据库，并执行建表 SQL。
        with self.write_connection() as connection:
            connection.execute(schema_sql)

    # 函数中使用了 yield，所以它是一个生成器函数。
    # @contextmanager 让这个生成器函数可以配合 with 使用。
    @contextmanager
    def connection(self, *, read_only: bool = False):
        """打开数据库连接，用完后自动关闭。"""

        # read_only=True 表示只读，不允许修改数据库。
        database_connection = duckdb.connect(
            str(self.path),
            read_only=read_only,
        )

        try:
            # 把连接交给 with 代码块使用。
            yield database_connection
        finally:
            # 无论代码是否报错，离开 with 代码块时都会关闭连接。
            database_connection.close()

    # 这个函数也使用了 yield，所以同样使用 @contextmanager。
    @contextmanager
    def write_connection(self):
        """打开可写连接，并保证同一时间只有一个写操作。"""

        # 第 1 步：申请写入锁。
        # 如果其他线程正在写数据库，当前线程会在这里等待。
        with self._write_lock:
            # 第 2 步：取得锁以后，打开一个普通的可写连接。
            with self.connection() as database_connection:
                # 第 3 步：把连接交给外层 with 代码块使用。
                yield database_connection

            # 第 4 步：离开内层 with，数据库连接已经自动关闭。

        # 离开外层 with，写入锁已经自动释放。
