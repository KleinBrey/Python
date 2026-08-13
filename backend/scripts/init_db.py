from backend.app.core.config import get_settings
from backend.app.database import DuckDBDatabase


def main() -> None:
    database = DuckDBDatabase(get_settings().database_path)
    database.initialize()
    print(f"DuckDB 已初始化: {database.path}")


if __name__ == "__main__":
    main()

