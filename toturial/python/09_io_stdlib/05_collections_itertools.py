"""
==================================================
知识点：collections 与 itertools
==================================================
"""

from collections import Counter, defaultdict, deque
from itertools import chain, combinations, islice

symbols = ["600519", "000001", "600519", "300750"]
counts = Counter(symbols)
print(counts, counts.most_common(2))

# defaultdict 在键首次访问时自动创建默认值，适合分组。
by_market: defaultdict[str, list[str]] = defaultdict(list)
for symbol in symbols:
    market = "SH" if symbol.startswith("6") else "SZ"
    by_market[market].append(symbol)
print(dict(by_market))

# deque 两端添加/删除都高效，常用于队列和固定长度滑动窗口。
latest_prices: deque[float] = deque(maxlen=3)
for price in [10.1, 10.2, 10.3, 10.4]:
    latest_prices.append(price)
print(latest_prices)

# itertools 返回惰性迭代器，适合组合或大数据流。
print(list(chain([1, 2], [3, 4])))
print(list(combinations(["A", "B", "C"], 2)))
print(list(islice(range(1_000_000), 3)))

"""
本节总结：Counter 计数、defaultdict 分组、deque 做队列；itertools 组合惰性流程。
"""
