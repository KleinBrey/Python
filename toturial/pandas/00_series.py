"""Pandas 第 0 课：用 Series 和 DataFrame 表示股票数据。"""

import pandas as pd
import numpy as np

# ------------------------------------------------------------------
# Series
# ------------------------------------------------------------------

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


"""sort_values()"""
# 对 Series 中的元素进行排序（按值排序）
price = pd.Series(
    [30, 10, 20],
    index=["A", "B", "C"],
)

print(price.sort_values())

# B    10
# C    20
# A    30
# dtype: int64

price.sort_values(ascending=False)


"""sort_index()"""
# 对 Series 的索引进行排序
price = pd.Series(
    [100, 200, 300],
    index=["600519", "000001", "300750"],
)


print(price.sort_index())

# B    10
# C    20
# A    30
# dtype: int64

price.sort_index(ascending=False)
print(price)


"""dropna()"""
# 删除 Series 中的缺失值（NaN）
s = pd.Series([10, np.nan, 20, np.nan, 30])

print(s.dropna())


"""fillna(value)"""
# 填充 Series 中的缺失值（NaN）
s = pd.Series([10, np.nan, 20])

print(s.fillna(0))


"""replace(to_replace, value)"""
# 替换 Series 中指定的值
market = pd.Series(
    [
        "主板",
        "创业板",
        "科创板",
    ]
)

print(market.replace("科创板", "STAR"))


"""cumsum()"""
# 返回 Series 的累计求和
profit = pd.Series([10, -5, 20, -8])

print(profit.cumsum())
# 0    10
# 1     5
# 2    25
# 3    17
# dtype: int64


"""cumprod()"""
# 返回 Series 的累计乘积
returns = pd.Series(
    [
        0.10,
        -0.05,
        0.03,
    ]
)

print((1 + returns).cumprod())
# 0    1.10000
# 1    1.04500
# 2    1.07635
# dtype: float64


"""shift(periods)"""
# 将 Series 中的元素按指定的步数进行位移
close = pd.Series(
    [
        10,
        11,
        12,
        15,
    ],
)

# 日期        昨天价格   今天价格
# 8月18日     NaN        10
# 8月19日     10         11
# 8月20日     11         12
# 8月21日     12         15

# 8月21日当天，昨天的收盘价是12，今天的收盘价是15


print(close.shift(1))

# 收益率 = 今天的收盘价 / 昨天的收盘价
daily_return = close / close.shift(1) - 1

# 计算今日相比较昨日的收益率
print(daily_return == close.pct_change())


"""rank()"""
# 返回 Series 中元素的排名
hot = pd.Series(
    [100, 30, 80, 20],
    index=["贵州茅台", "平安银行", "宁德时代", "招商银行"],
)

print(hot.rank())

# 默认是 数值越小 → 排名越靠前
# 所以招商银行是20，数字最小，排名是1 ...

# 贵州茅台    4
# 平安银行    2
# 宁德时代    3
# 招商银行    1


"""to_list()"""
# 将 Series 转换为 Python 列表
symbols = pd.Series(
    [
        "600519",
        "000001",
        "300750",
    ]
)

result = symbols.to_list()

print(result)


"""to_frame()"""
# 将 Series 转换为 DataFrame
s = pd.Series(
    [10, 20, 30],
    name="close",
)

frame = s.to_frame()

print(frame)


"""iloc[]"""
# 通过位置索引来选择数据
s = pd.Series(
    [10.5, 11.2, 12.8],
    index=["600519", "000001", "300750"],
)

# 取第一个
print(s.iloc[0])

# 取第二个
print(s.iloc[1])

# 取前两个
print(s.iloc[:2])


"""loc[]"""
# 通过标签索引来选择数据
s = pd.Series(
    [10.5, 11.2, 12.8],
    index=["600519", "000001", "300750"],
)

# 取"600519"索引对应的
print(s.loc["600519"])
