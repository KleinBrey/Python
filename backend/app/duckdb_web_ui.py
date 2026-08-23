from backend.app.database import DuckDBDatabase

# 初始化数据库
database = DuckDBDatabase()
database.initialize()

# 开启可视化Web页面
database.start_ui()

try:
    # DuckDB UI 依赖当前 Python 程序。
    # 等待用户按回车，防止程序退出后 UI 页面变成空白。
    input("DuckDB UI 已启动：http://localhost:4213/\n按回车键关闭 UI：")
finally:
    database.stop_ui()
