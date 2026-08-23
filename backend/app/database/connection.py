from pathlib import Path

import duckdb

# 项目根目录：从当前文件所在目录往上三级
PROJECT_ROOT = Path(__file__).resolve().parents[3]

database_path: Path = PROJECT_ROOT / "data" / "market.duckdb"

schema_path = Path(__file__).parent / "schema.sql"


class DuckDBDatabase:

    def __init__(self):
        # 把数据库路径转换成完整的绝对路径。
        self.database_path = Path(database_path).expanduser().resolve()
        self.schema_path = schema_path
        # UI 必须一直使用同一个连接。
        # 只要这个连接没有关闭，UI 页面就可以继续工作。
        self._ui_connection = None

    # 初始化duckdb
    def initialize(self) -> None:

        # 如果数据库所在的文件夹不存在，就自动创建它。
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

        # 获取初始化SQL脚本
        schema_sql = self.schema_path.read_text(encoding="utf-8")

        # 创建表以后，自动关闭这次普通连接。
        with self.connection() as connection:
            connection.execute(schema_sql)

    def connection(self, *, read_only: bool = False):
        # 每次数据库操作都创建一个普通连接。
        # with 代码块结束时，这个连接会自动关闭。
        connection = duckdb.connect(
            str(self.database_path),
            read_only=read_only,
        )
        return connection

    def start_ui(self):
        # 避免重复启动 UI。
        if self._ui_connection is not None:
            return

        # UI 使用独立长连接，不能被普通数据库操作覆盖。
        self._ui_connection = duckdb.connect(str(self.database_path))
        self._ui_connection.execute("INSTALL ui")
        self._ui_connection.execute("LOAD ui")
        self._ui_connection.execute("CALL start_ui()")

    def stop_ui(self):
        if self._ui_connection is not None:
            self._ui_connection.execute("CALL stop_ui_server()")
            self._ui_connection.close()
            self._ui_connection = None
