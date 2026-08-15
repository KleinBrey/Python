from database.connection import DuckDBDatabase
from provider.hithink import Provider

# 初始化数据库
database = DuckDBDatabase()
database.initialize()

# 获取API数据
providerInstant = Provider()
stock_list = providerInstant.fetch_stock_list()

print(stock_list)


with database.connection() as connection:
    connection.execute("""
        INSERT INTO stocks (symbol, name, exchange, type, source)
        SELECT symbol, name, exchange, type, source
        FROM stock_list
        ON CONFLICT (symbol) DO UPDATE SET
            name = excluded.name,
            exchange = excluded.exchange,
            type = excluded.type,
            source = excluded.source,
            update_time = now()
        """)

    total = connection.execute("SELECT COUNT(*) FROM stocks").fetchone()[0]

print(f"成功处理 {len(stock_list)} 行，数据库中共有 {total} 行。")
