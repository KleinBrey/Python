"""Pandas 第 0 课：用 Series 和 DataFrame 表示股票数据。"""

import pandas as pd

# Series 是“一列带标签的数据”。这里用交易日期作为标签。
series = pd.Series(
    ["300645", pd.NA, "688431"],
    index=[123, "2026-08-14", "测试"],
    name="symbol",
)

"""index"""

# index 获取 Series 的索引。 注意：它是属性，不是方法，所以没有 ()

print(series.index)  # Index([123, '2026-08-14', '测试'], dtype='object')

# 转成普通数组
print(series.index.to_list())  # [123, '2026-08-14', '测试']

"""values"""

# values 获取 Series 的数据部分，返回 NumPy 数组。 注意：它是属性，不是方法，所以没有 ()

print(series.values)  # ['300645' <NA> '688431']

# 虽然他们在终端长得一样，但是类型不一样，一个是numpy数组，一个是普通list
print(
    type(series.values), type(series.index.to_list())
)  # <class 'numpy.ndarray'> <class 'list'>


"""head(n)"""
# 取前 n 条。
print(series.head(2))

# 不传值默认前5条
print(series.head())

"""tail(n)"""
# 取最后 n 条
print(series.tail(2))

# 不传值默认后5条
print(series.tail())


"""dtype"""
# 返回 Series 中数据的类型
print(series.dtype)  # object


"""shape"""
# 返回 Series 的形状（行数）
# 返回的是一个元组
print(series.shape)  # (3,)


"""describe()"""
# 返回 Series 的统计描述（如均值、标准差、最小值等）
print(series.describe())
# count          2
# unique         2
# top       300645
# freq           1
# Name: symbol, dtype: object


"""isnull()"""
# 返回一个布尔 Series，表示每个元素是否为 NaN
print(series.isnull())
# 123            False
# 2026-08-14     True
# 测试            False
# Name: symbol, dtype: bool


"""notnull()"""
# 返回一个布尔 Series，表示每个元素是否不是 NaN
print(series.notnull())
# 123            True
# 2026-08-14     False
# 测试            True
# Name: symbol, dtype: bool


"""unique()"""
# 返回 Series 中的唯一值（去重）
market = pd.Series(["主板", "创业板", "主板", "科创板", "创业板"])

print(market.unique())  # ['主板' '创业板' '科创板']


"""value_counts()"""
# 返回 Series 中每个唯一值的出现次数,返回的是一个Series
market = pd.Series(["主板", "创业板", "主板", "科创板", "创业板"])

print(market.value_counts())
# 主板      2
# 创业板    2
# 科创板    1
# Name: count, dtype: int64


"""map(func)"""
# 将指定函数应用于 Series 中的每个元素
symbols = pd.Series(
    [
        "600519.SH",
        "000001.SZ",
        "300750.SZ",
    ]
)

result = symbols.map(lambda x: x.split(".")[0])

# 不过这种字符串处理，更推荐：
# result = symbols.str.split(".").str[0]

print(result)
# 0    600519
# 1    000001
# 2    300750
# dtype: object


# map() 特别适合字典映射。
exchange_map = {
    "SSE": "SH",
    "SZSE": "SZ",
    "BSE": "BJ",
}

exchange = pd.Series(
    [
        "SSE",
        "SZSE",
        "BSE",
    ]
)

print(exchange.map(exchange_map))
# 0    SH
# 1    SZ
# 2    BJ
# dtype: object


"""apply(func)"""
# 将指定函数应用于 Series 中的每个元素，常用于自定义操作
price = pd.Series([10, 20, 30])

result = price.apply(lambda x: x * 1.1)

print(result)
# 0    11.0
# 1    22.0
# 2    33.0
# dtype: float64


"""astype(dtype)"""
# 将 Series 转换为指定的类型
volume = pd.Series(
    [
        "1000",
        "2000",
        "3000",
    ]
)

print(volume.dtype)  # object
volume = volume.astype(int)

print(volume)
print(volume.dtype)


# DataFrame 是二维表，也是 Pandas 中最常用的数据结构。
# bars = pd.DataFrame(
#     {
#         "symbol": ["600519.SH", "000001.BJ", "300750.SZ"],
#         "name": ["贵州茅台", "平安银行", "宁德时代"],
#         "close": [1488.0, 11.4, 300.0],
#         "volume": [1680, 11800, 5600],
#     }
# )

# data_list = [
#     {
#         "symbol": "600519.SH",
#         "name": "贵州茅台",
#         "close": 1488.0,
#         "volume": 1680,
#     },
#     {
#         "symbol": "000001.BJ",
#         "name": "平安银行",
#         "close": 11.4,
#         "volume": 11800,
#     },
#     {
#         "symbol": "300750.SZ",
#         "name": "宁德时代",
#         "close": 300.0,
#         "volume": 5600,
#     },
# ]

# data_dict = {
#     "symbol": ["600519.SH", "000001.BJ", "300750.SZ"],
#     "name": ["贵州茅台", "平安银行", "宁德时代"],
#     "close": [1488.0, 11.4, 300.0],
#     "volume": [1680, 11800, 5600],
# }

# bars = pd.DataFrame(data_list)

# bars_2 = pd.DataFrame(data_dict)

# print(f"两个frame是否相等: {bars.equals(bars_2)}")

# print("\n=== 最新行情表 ===")
# print(bars)
# print("\n行数、列数：", bars.shape)
# print("列名：", bars.columns.tolist())
# print("收盘价这一列：\n", bars["close"])


# 记住：一列通常是 Series，多列组成 DataFrame。
