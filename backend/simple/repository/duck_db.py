"""DuckDB 数据仓库层。

Repository（仓库）负责集中处理数据库的增、删、改、查。
其他代码只需要调用这里的方法，不需要重复编写 SQL。
"""

import pandas as pd

from backend.simple.database import DuckDBDatabase


class BaseRepository:
    """提供所有数据表都能使用的基础增、删、改、查方法。"""

    def __init__(self, db: DuckDBDatabase, table_name: str):
        """保存数据库对象和需要操作的表名。"""

        self.db = db
        self.table_name = table_name

    def insert(self, rows: pd.DataFrame) -> bool:
        """插入数据，成功返回 True，失败返回 False。"""

        if rows.empty:
            return False

        try:
            column_names = rows.columns.tolist()
            columns_sql = ", ".join(column_names)

            sql = f"""
                INSERT INTO {self.table_name} ({columns_sql})
                SELECT {columns_sql}
                FROM temporary_rows
                ON CONFLICT (symbol) DO UPDATE SET
                    name = excluded.name,
                    exchange = excluded.exchange,
                    type = excluded.type,
                    source = excluded.source,
                    update_time = now()
            """

            with self.db.connection() as connection:
                # 把 DataFrame 注册成 DuckDB 可以查询的临时表。
                connection.register("temporary_rows", rows)
                connection.execute(sql)
                total = connection.execute(
                    f"SELECT COUNT(*) FROM {self.table_name}"
                ).fetchone()[0]
                print(f"成功处理 {len(rows)} 行，数据库中共有 {total} 行。")

            return True

        except Exception as error:
            print(f"插入失败：{error}")
            return False


class StockRepository(BaseRepository):
    """stocks 表专用的 Repository。"""

    def __init__(self, db: DuckDBDatabase):
        """指定这个 Repository 操作 stocks 表。"""

        super().__init__(db, "stocks")

    def insert_stocks(self, rows) -> bool:
        """把股票 DataFrame 写入 stocks 表。"""

        return self.insert(rows)
