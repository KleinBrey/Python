"""
==================================================
知识点：sqlite3 与 SQL CRUD
==================================================

SQLite 随 Python 提供、数据库可存单个文件；本例使用内存数据库，运行后不留文件。
CRUD = Create/Read/Update/Delete，对应 INSERT/SELECT/UPDATE/DELETE。
"""

import sqlite3

with sqlite3.connect(":memory:") as connection:
    connection.row_factory = sqlite3.Row  # 查询结果可按列名访问
    connection.execute(
        """
        CREATE TABLE stocks (
            symbol TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL CHECK (price > 0)
        )
        """
    )

    # ? 是参数占位符。永远不要用 f-string 拼接用户输入，否则会有 SQL 注入风险。
    connection.execute(
        "INSERT INTO stocks (symbol, name, price) VALUES (?, ?, ?)",
        ("600519", "贵州茅台", 1688.0),
    )
    connection.executemany(
        "INSERT INTO stocks VALUES (?, ?, ?)",
        [("000001", "平安银行", 10.5), ("300750", "宁德时代", 220.0)],
    )

    rows = connection.execute(
        "SELECT symbol, name, price FROM stocks WHERE price > ? ORDER BY price DESC",
        (100,),  # 单元素 tuple 的逗号不能省
    ).fetchall()
    for row in rows:
        print(dict(row))

    connection.execute("UPDATE stocks SET price = ? WHERE symbol = ?", (1690.0, "600519"))
    connection.execute("DELETE FROM stocks WHERE symbol = ?", ("000001",))
    connection.commit()
    print("剩余行数：", connection.execute("SELECT COUNT(*) FROM stocks").fetchone()[0])

# with 会提交正常事务或回滚异常事务，但连接关闭行为因对象协议需留意；
# 本例进程结束会释放内存连接，持久项目可显式 connection.close()。

"""
本节总结：SQL 参数必须使用占位符；事务保证一组更改的一致性；SQLite 适合轻量本地应用。
"""
