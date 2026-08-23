from backend.app.database import DuckDBDatabase


def main() -> None:
    database = DuckDBDatabase()
    database.initialize()
    print(f"DuckDB 已初始化: {database.database_path}")


if __name__ == "__main__":
    main()
