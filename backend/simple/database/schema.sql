-- 股票基础信息表：每只股票保存一条记录。
CREATE TABLE IF NOT EXISTS stocks (
  symbol VARCHAR PRIMARY KEY,
  name VARCHAR NOT NULL,
  exchange VARCHAR NOT NULL,
  type VARCHAR NOT NULL DEFAULT 'a-share',
  source VARCHAR NOT NULL,
  -- 记录更新时间；插入时未指定则使用数据库当前时间。
  update_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);