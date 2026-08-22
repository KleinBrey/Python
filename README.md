# quant-platform

本地 A 股行情数据底座。第一阶段只维护全市场最近一年的**不复权日 K**，为后续可视化、因子计算、量化选股和回测提供统一数据入口。


## 结构

```text
quant-platform/
├── backend/
│   ├── app/
│   │   ├── api/             # FastAPI 路由
│   │   ├── core/            # 配置
│   │   ├── database/        # DuckDB 连接与 DDL
│   │   ├── providers/       # HiThink Financial API
│   │   ├── repositories/    # DuckDB 读写
│   │   ├── services/        # 清洗与同步业务
│   │   ├── jobs/            # 定时更新和校准
│   │   ├── schemas/         # Pydantic 模型
│   │   └── main.py
│   ├── scripts/
│   ├── tests/
│   └── .env
├── frontend/                # 原 React + Vite 前端，本次未修改
├── data/
│   └── market.duckdb
├── pyproject.toml           # Python 依赖与项目配置的唯一来源
├── uv.lock                  # uv 生成的可复现依赖锁文件
└── README.md
```


## 安装

要求 Python 3.11+ 和 [uv](https://docs.astral.sh/uv/getting-started/installation/)。

```bash
cd 当前项目地址
rm -rf .venv
uv sync
```

运行依赖和开发依赖统一在根目录 `pyproject.toml` 中声明，精确版本由 `uv.lock` 锁定。`uv sync` 会创建 `.venv` 并默认安装 `dev` 依赖组。

如果你还想手动激活，重新生成后：

```bash
source .venv/bin/activate
```

再：

```bash
echo $VIRTUAL_ENV
```

## 初始化与同步

```bash
# 创建 market.duckdb 和表
uv run python backend/scripts/init_db.py

# 小批量试跑
uv run quant-sync \
  --mode initial --symbols 000001,600519

# 初始化全市场最近一年日 K
uv run quant-sync --mode initial
```

全市场任务逐只写入，单只失败不会回滚其他股票。重新执行会幂等覆盖，可安全断点续跑。可用 `--limit 20` 限制试跑数量。

同步模式：

- `daily`：从每只股票本地最新日期向前回看 5 个自然日后增量更新；
- `weekly`：重新校准数据库最近 60 个交易日；
- `monthly`：重新校准最近一年；
- `initial`：初始化最近一年。

## 定时任务

FastAPI 默认内置 APScheduler：

- 周一至周五 18:00：每日增量；
- 周六 09:00：最近 60 个交易日校准；
- 每月 1 日 10:00：最近一年校准。

时间和开关可在 `backend/.env` 调整。节假日即使触发，空响应也不会生成伪交易日。也可设置 `SCHEDULER_ENABLED=false`，再由系统 Cron 调用同步脚本。

## 启动 API

```bash
uv run uvicorn backend.app.main:app \
  --host 127.0.0.1 --port 8001 --reload
```

- Swagger：<http://127.0.0.1:8001/docs>
- `GET /api/health`
- `GET /api/market/status`
- `GET /api/stocks?query=茅台`
- `GET /api/market/bars/600519.SH`
- `POST /api/jobs/run?mode=daily`

## 验证

```bash
uv run pytest
```

数据仅用于研究，不构成投资建议。
