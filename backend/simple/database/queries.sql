-- DuckDB 常用增删改查语句。
--
-- 在 DuckDB UI 中，表可以使用完整名称 "simple".main.daily_bars；
-- 在应用连接中，也可以直接使用 daily_bars。
-- 文件中的语句会真实修改数据库，请选中需要的单条语句执行。

-- ============================================================
--                             增
-- ============================================================

-- 新增一条日线数据
INSERT INTO "simple".main.daily_bars (
  symbol,
  date,
  open,
  high,
  low,
  close,
  volume,
  amount,
  source
) VALUES (
  '601899',
  DATE '2026-08-18',
  25.10,
  25.80,
  24.90,
  25.50,
  1000000,
  25300000,
  'manual'
);

-- 增或改：主键已存在时更新，不存在时新增。
INSERT INTO "simple".main.daily_bars (
  symbol,
  date,
  open,
  high,
  low,
  close,
  volume,
  amount,
  source
) VALUES (
  '601899',
  DATE '2026-08-18',
  25.10,
  25.80,
  24.90,
  25.60,
  1000000,
  25400000,
  'manual'
)
ON CONFLICT (symbol, date) DO UPDATE SET
  open = excluded.open,
  high = excluded.high,
  low = excluded.low,
  close = excluded.close,
  volume = excluded.volume,
  amount = excluded.amount,
  source = excluded.source,
  update_time = now();

-- ============================================================
--                            删
-- ============================================================

--删除指定股票、指定日期的数据
DELETE FROM "simple".main.daily_bars
WHERE symbol = '601899'
  AND date = DATE '2026-08-18';

-- ============================================================
--                            改
-- ============================================================

-- 更新指定股票、指定日期的数据
UPDATE "simple".main.daily_bars
SET close = 25.60,
    amount = 25400000,
    update_time = now()
WHERE symbol = '601899'
  AND date = DATE '2026-08-18';

-- ============================================================
--                            查询
-- ============================================================

-- 查询股票基础信息。
SELECT *
FROM "simple".main.stocks
WHERE symbol = '601899';

-- 查询指定股票的日线数据（最新交易日在前）
SELECT *
FROM "simple".main.daily_bars
WHERE symbol = '601899'
ORDER BY date DESC;

-- 查询指定股票最近 30 条日线数据。
SELECT *
FROM "simple".main.daily_bars
WHERE symbol = '601899'
ORDER BY date DESC
LIMIT 30;

-- 按日期范围查询。
SELECT *
FROM "simple".main.daily_bars
WHERE symbol = '601899'
  AND date BETWEEN DATE '2026-01-01' AND DATE '2026-12-31'
ORDER BY date DESC;


