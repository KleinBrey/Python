import numpy as np
from datetime import datetime, date

def clean_mongo_data(data):
    """将数据中的 numpy 类型和 date 类型转换为 Python 原生类型"""

    def clean_value(value):
        if isinstance(value, (np.integer, np.int64, np.int32)):
            return int(value)
        elif isinstance(value, (np.floating, np.float64, np.float32)):
            return float(value)
        elif isinstance(value, (np.bool_)):
            return bool(value)
        elif isinstance(value, date) and not isinstance(value, datetime):
            return datetime.combine(value, datetime.min.time())
        elif isinstance(value, dict):
            return {k: clean_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [clean_value(v) for v in value]
        else:
            return value

    return [clean_value(record) for record in data]