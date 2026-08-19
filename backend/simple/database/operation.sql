-- DuckDB 常用增删改查语句。

-- SQL 里双引号 " 表示字段名/表名，字符串要用单引号 '

-- 默认 stocks 和 daily 两张表



-- ============================================================
--                            查询
-- ============================================================

-- 查询指定股票基础信息
SELECT *
FROM stocks
WHERE symbol = '601899';

-- 查询指定股票的 date字段（升序）
SELECT *
FROM daily
WHERE symbol = '601899'
ORDER BY date ASC;

-- 查询指定股票的 date字段（降序）
SELECT *
FROM daily
WHERE symbol = '601899'
ORDER BY date DESC;

-- 查询指定股票最近 30 条日线数据。
SELECT *
FROM daily
WHERE symbol = '601899'
ORDER BY date DESC
LIMIT 30;

-- 按日期范围查询。
SELECT *
FROM daily
WHERE symbol = '601899'
  AND date BETWEEN DATE '2026-01-01' AND DATE '2026-12-31'
ORDER BY date DESC;

-- 两张表拼接起来
SELECT
    stocks.symbol,
    stocks.name,
    daily.close
FROM stocks
JOIN daily
    ON stocks.symbol = daily.symbol;




-- ============================================================
--                             增
-- ============================================================

-- 新增一条数据
INSERT INTO stocks (
    symbol,
    name,
    exchange,
    source
)
VALUES (
    '601899',
    '紫金矿业',
    'SH',
    'Tushare'
);

-- 增或改：主键已存在时更新，不存在时新增。
INSERT INTO daily (
  symbol,
  date,
  open,
  high,
  low,
  close,
) 
VALUES (
  '601899',
  DATE '2026-08-18',
  25.10,
  25.80,
  24.90,
  25.60,
)
ON CONFLICT (symbol, date) DO UPDATE SET
  open = excluded.open,
  high = excluded.high,
  low = excluded.low,
  close = excluded.close,
  update_time = now();


-- ============================================================
--                            改
-- ============================================================

-- 更新指定股票、指定日期的数据
UPDATE daily
SET close = 25.60,
    amount = 25400000,
    update_time = now()
WHERE symbol = '601899'
  AND date = DATE '2026-08-18';




-- ============================================================
--                            删
-- ============================================================

-- 删除整张表
DELETE FROM daily;

--删除指定股票、指定日期的数据
DELETE FROM daily
WHERE symbol = '601899'
AND date = DATE '2026-08-18';



