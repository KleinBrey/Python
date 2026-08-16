"""
Repository 层：数据访问对象（DAO）。
负责所有数据库操作的封装。
"""

from backend.simple.repository.duck_db import BaseRepository, StockRepository

__all__ = ["BaseRepository", "StockRepository"]
