import numpy as np
import pandas as pd
from datetime import datetime, date
from bson import ObjectId


def to_mongo_format(data):
    """
    将 Python / Numpy / Pandas 类型 转换为 MongoDB 可接受的类型
    """
    def convert(value):
        if isinstance(value, dict):
            return {k: convert(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [convert(v) for v in value]
        elif isinstance(value, (np.integer,)):
            return int(value)
        elif isinstance(value, (np.floating,)):
            return float(value)
        elif isinstance(value, (np.bool_,)):
            return bool(value)
        elif isinstance(value, (np.ndarray,)):
            return value.tolist()
        elif isinstance(value, (pd.Timestamp,)):
            return value.to_pydatetime()
        elif isinstance(value, date) and not isinstance(value, datetime):
            return datetime.combine(value, datetime.min.time())
        elif isinstance(value, ObjectId):
            return value
        else:
            return value

    if isinstance(data, list):
        return [convert(item) for item in data]
    else:
        return convert(data)


def from_mongo_format(data):
    """
    将 MongoDB 取出的数据 转换为 Python / Numpy / Pandas 常用类型
    """
    def convert(value):
        if isinstance(value, dict):
            return {k: convert(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [convert(v) for v in value]
        elif isinstance(value, float):
            return np.float64(value)
        elif isinstance(value, int):
            return np.int64(value)
        elif isinstance(value, bool):
            return np.bool_(value)
        elif isinstance(value, datetime):
            return pd.Timestamp(value)
        elif isinstance(value, ObjectId):
            return str(value)   # 转成字符串更方便分析
        else:
            return value

    if isinstance(data, list):
        return [convert(item) for item in data]
    else:
        return convert(data)
