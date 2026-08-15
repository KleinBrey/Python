-- 股票基础信息表：每只股票保存一条记录。
CREATE TABLE IF NOT EXISTS stocks (
  symbol VARCHAR PRIMARY KEY,
  name VARCHAR NOT NULL,
  exchange VARCHAR NOT NULL,
  type VARCHAR NOT NULL DEFAULT 'a-share',
  source VARCHAR NOT NULL,
  -- 记录更新时间；插入时未指定则使用数据库当前时间。
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 日 K 线表：保存股票在每个交易日、每种复权方式下的行情数据。
CREATE TABLE IF NOT EXISTS daily_bars (
  -- 股票唯一标识，对应 stocks.symbol。
  symbol VARCHAR NOT NULL,
  -- 交易日期。
  trade_date DATE NOT NULL,
  -- 开盘价。
  open DOUBLE NOT NULL,
  -- 最高价。
  high DOUBLE NOT NULL,
  -- 最低价。
  low DOUBLE NOT NULL,
  -- 收盘价。
  close DOUBLE NOT NULL,
  -- 前一交易日收盘价。
  pre_close DOUBLE,
  -- 涨跌额，通常等于 close - pre_close。
  change DOUBLE,
  -- 涨跌幅，具体单位由数据源约定。
  pct_change DOUBLE,
  -- 成交量，不允许为负数。
  volume DOUBLE NOT NULL,
  -- 成交额。
  amount DOUBLE,
  -- 复权方式，例如 none、forward 或 backward；默认不复权。
  adjustment VARCHAR NOT NULL DEFAULT 'none',
  -- 该条行情数据的来源。
  source VARCHAR NOT NULL,
  -- 数据写入数据库的时间。
  ingested_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  -- 同一股票、交易日和复权方式只能存在一条记录。
  PRIMARY KEY (symbol, trade_date, adjustment),
  -- 最高价必须不低于开盘价、最高价、最低价和收盘价中的任意值。
  CHECK (high >= greatest(open, high, low, close)),
  -- 最低价必须不高于开盘价、最高价、最低价和收盘价中的任意值。
  CHECK (low <= least(open, high, low, close)),
  -- 成交量不能为负数。
  CHECK (volume >= 0)
);

-- 加快按交易日期查询全部股票行情的速度。
CREATE INDEX IF NOT EXISTS idx_daily_bars_date ON daily_bars (trade_date);

-- 加快按股票和日期范围查询历史行情的速度。
CREATE INDEX IF NOT EXISTS idx_daily_bars_symbol_date ON daily_bars (symbol, trade_date);

-- 为同步任务生成连续递增的 ID。
CREATE SEQUENCE IF NOT EXISTS sync_runs_id_seq START 1;

-- 数据同步运行记录表：用于跟踪每次同步任务的进度和结果。
CREATE TABLE IF NOT EXISTS sync_runs (
  -- 同步任务的唯一 ID，由序列自动生成。
  id BIGINT PRIMARY KEY DEFAULT nextval('sync_runs_id_seq'),
  -- 同步模式，例如 initial（初始化）或 daily（每日增量）。
  mode VARCHAR NOT NULL,
  -- 任务状态，例如 running、success、partial 或 failed。
  status VARCHAR NOT NULL,
  -- 任务开始时间。
  started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  -- 任务结束时间；尚未结束时为空。
  finished_at TIMESTAMP,
  -- 本次计划同步的股票总数。
  symbols_total INTEGER NOT NULL DEFAULT 0,
  -- 同步成功的股票数量。
  symbols_succeeded INTEGER NOT NULL DEFAULT 0,
  -- 同步失败的股票数量。
  symbols_failed INTEGER NOT NULL DEFAULT 0,
  -- 本次任务累计写入的行情记录数。
  rows_written BIGINT NOT NULL DEFAULT 0,
  -- 任务说明、错误信息或其他补充消息。
  message VARCHAR
);