CREATE TABLE IF NOT EXISTS stocks (
    symbol VARCHAR PRIMARY KEY,
    code VARCHAR NOT NULL,
    exchange VARCHAR NOT NULL,
    name VARCHAR,
    asset_type VARCHAR NOT NULL DEFAULT 'a-share',
    source VARCHAR NOT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS daily_bars (
    symbol VARCHAR NOT NULL,
    trade_date DATE NOT NULL,
    open DOUBLE NOT NULL,
    high DOUBLE NOT NULL,
    low DOUBLE NOT NULL,
    close DOUBLE NOT NULL,
    pre_close DOUBLE,
    change DOUBLE,
    pct_change DOUBLE,
    volume DOUBLE NOT NULL,
    amount DOUBLE,
    adjustment VARCHAR NOT NULL DEFAULT 'none',
    source VARCHAR NOT NULL,
    ingested_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (symbol, trade_date, adjustment),
    CHECK (high >= greatest(open, high, low, close)),
    CHECK (low <= least(open, high, low, close)),
    CHECK (volume >= 0)
);

CREATE INDEX IF NOT EXISTS idx_daily_bars_date ON daily_bars(trade_date);
CREATE INDEX IF NOT EXISTS idx_daily_bars_symbol_date ON daily_bars(symbol, trade_date);

CREATE SEQUENCE IF NOT EXISTS sync_runs_id_seq START 1;
CREATE TABLE IF NOT EXISTS sync_runs (
    id BIGINT PRIMARY KEY DEFAULT nextval('sync_runs_id_seq'),
    mode VARCHAR NOT NULL,
    status VARCHAR NOT NULL,
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP,
    symbols_total INTEGER NOT NULL DEFAULT 0,
    symbols_succeeded INTEGER NOT NULL DEFAULT 0,
    symbols_failed INTEGER NOT NULL DEFAULT 0,
    rows_written BIGINT NOT NULL DEFAULT 0,
    message VARCHAR
);

