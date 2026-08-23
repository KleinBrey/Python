# quant-platform

本地 A 股数据平台，使用 FastAPI、DuckDB、Pandas 和 APScheduler，提供股票基础信息、日 K、股票热度同步以及量化策略实验能力。

## 项目结构

```text
quant-platform/
├── backend/
│   ├── app/
│   │   ├── api/             # FastAPI 路由和依赖
│   │   ├── config/          # 应用与调度配置
│   │   ├── database/        # DuckDB 连接、表结构和辅助 SQL
│   │   ├── jobs/            # 定时任务
│   │   ├── provider/        # Tushare、HiThink、AkShare、问财
│   │   ├── repository/      # DuckDB 数据访问
│   │   ├── schemas/         # Pydantic API 模型
│   │   ├── scripts/         # 各类数据同步脚本
│   │   ├── services/        # 数据格式化和同步业务
│   │   ├── strategy/        # 选股策略
│   │   ├── utils/           # 日期、股票代码工具
│   │   ├── view/            # Rich 命令行展示
│   │   └── main.py          # FastAPI 入口
│   ├── scripts/             # 命令行入口包装
│   ├── tests/               # 后端测试
│   └── run.py               # API 快捷启动入口
├── data/
│   └── market.duckdb
├── frontend/
├── pyproject.toml
└── README.md
```

## 安装

要求 Python 3.11+ 和 [uv](https://docs.astral.sh/uv/getting-started/installation/)。

```bash
uv sync
```

Tushare 配置从 `backend/.env` 或环境变量读取：

```dotenv
TUSHARE_PRIVATE_TOKEN=
TUSHARE_RELAY_TOKEN=
TUSHARE_USE_RELAY=true
TUSHARE_RELAY_URL=https://t.xiaodefa.top
```

调度器可通过以下配置调整：

```dotenv
SCHEDULER_ENABLED=true
SCHEDULER_TIMEZONE=Asia/Shanghai
DAILY_UPDATE_HOUR=18
DAILY_UPDATE_MINUTE=0
```

## 初始化和同步

初始化 `data/market.duckdb`：

```bash
uv run python -m backend.scripts.init_db
```

同步股票列表、日 K 和当日股票热度：

```bash
uv run python -m backend.app.scripts.sync_stock_list_db
uv run quant-sync --lookback-days 3 --batch-size 100
uv run python -m backend.app.scripts.sync_stock_hot_db
```

日 K 常用回看范围：

- 日常更新：`--lookback-days 3 --batch-size 100`
- 每周校准：`--lookback-days 60 --batch-size 50`
- 年度范围：`--lookback-days 365 --batch-size 10`

## 启动 API

```bash
uv run quant-api
```

也可以直接启动 Uvicorn：

```bash
uv run uvicorn backend.app.main:app \
  --host 127.0.0.1 --port 8001 --reload
```

- Swagger：<http://127.0.0.1:8001/docs>
- `GET /api/stocks-list`：读取本地股票列表
- `POST /api/stocks-list`：从 Tushare 更新股票列表

## 定时任务

FastAPI 启动时默认注册以下任务：

- 每月 1 日 10:00：更新股票列表；
- 周一至周五 18:00：更新股票热度；
- 周一至周五配置时间：更新最近 3 个自然日的日 K；
- 每周六 09:00：校准最近 60 个自然日的日 K；
- 每月 1 日 10:00：校准最近 365 个自然日的日 K。

只运行调度器、不启动 API：

```bash
uv run python -m backend.scripts.run_scheduler
```

## 测试

```bash
uv run pytest
```

数据仅用于研究，不构成投资建议。
