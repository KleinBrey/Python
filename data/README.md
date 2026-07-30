# 统一数据层

`data/` 同时是数据接入源码目录和默认运行时数据根目录。供应商字段只能出现在
`providers/`，业务层通过 `service.py` 获取系统统一格式。

```text
data/
├── providers/
│   ├── hithink_financial.py  # 唯一结构化数据源
│   └── iwencai_api.py        # 仅自然语言选股
├── schemas.py                # 稳定字段契约
├── normalizers.py            # 字段、日期、单位、复权标准化
├── service.py                # 业务取数门面
├── registry.py               # 数据源能力与凭证元数据
├── hot_rankings.py           # 官方热榜注册
├── raw/
├── processed/
├── cache/
└── exports/
```

## 官方数据源

结构化数据统一使用 `hithink-financial`，Base URL 默认是
`https://fuyao.aicubes.cn`，凭证环境变量为
`HITHINK_FINANCE_API_KEY`。当前已接入：

- A 股代码表与标的检索
- 全市场或指定股票行情快照
- 日 K（不复权、前复权、后复权）
- 最新估值快照
- 24 小时/小时热股榜、日/小时飙升榜、涨停池
- 前端历史 K 线 JSON 转换

问财 OpenAPI 仅负责把自然语言条件转换为股票列表。列表中的行情、估值和 K 线
仍需通过 `hithink-financial` 获取。

## 统一格式

日 K 核心列：

```text
symbol, code, exchange, trade_date,
open, high, low, close, volume, amount,
frequency, adjustment, source, ingested_at
```

统一单位为：成交量“股”、成交额“元”，代码格式如 `600519.SH`，复权类型为
`none` / `qfq` / `hfq`。

```python
from data import fetch_daily_bars

bars = fetch_daily_bars(
    "hithink-financial",
    ["600519.SH", "000001.SZ"],
    "20260101",
    "20260725",
    adjustment="qfq",
)
```

扶摇目前未开放行业、上市状态、总股本和总市值字段；统一股票主数据仍保留这些列，
值为空，调用方不得从其他供应商补齐。

## 扩展约束

未来增加数据源时：

1. 在 `providers/` 增加供应商适配器。
2. 用 `normalizers.py` 转成既有稳定契约。
3. 在 `registry.py` 注册元数据和能力。
4. 只在 `service.py` 增加路由，不修改策略和存储代码。
