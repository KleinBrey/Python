import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { ClientSideRowModelModule, CellStyleModule, colorSchemeDark, themeQuartz } from 'ag-grid-community';
import { AgGridProvider, AgGridReact } from 'ag-grid-react';
import moment from 'moment';

import { getDailyBarsApi } from '@/api/quantide/api.js';
import StockKlineChart from '@/components/TradingView/StockKlineChart.jsx';
import styles from './StrategyResultsTable.module.css';

const modules = [ClientSideRowModelModule, CellStyleModule];
const themeDark = themeQuartz.withPart(colorSchemeDark).withParams({ backgroundColor: '#09090b' });
const KLINE_ROW_HEIGHT = 586;
const historyCache = new Map();

function finiteNumber(value) {
  if (value === null || value === undefined || value === '') return null;
  const number = Number(value);
  return Number.isFinite(number) ? number : null;
}

function formatNumber(value, digits = 2) {
  const number = finiteNumber(value);
  return number === null ? '-' : number.toFixed(digits);
}

function formatPercent(value) {
  const number = finiteNumber(value);
  if (number === null) return '-';
  const percent = number * 100;
  return `${percent > 0 ? '+' : ''}${percent.toFixed(2)}%`;
}

function formatPlainPercent(value) {
  const number = finiteNumber(value);
  return number === null ? '-' : `${(number * 100).toFixed(2)}%`;
}

function PercentCell({ value }) {
  const number = finiteNumber(value);
  const color = number > 0 ? '#f04451' : number < 0 ? '#24bd7a' : undefined;
  return <span style={{ color }}>{formatPercent(value)}</span>;
}

function formatMarketCap(value) {
  const number = finiteNumber(value);
  return number === null ? '-' : formatNumber(number / 1e8);
}

function transformHistory(items = []) {
  if (!Array.isArray(items)) return [];
  return items.map(item => ({
    date: item.trade_date,
    open: Number(item.open.toFixed(2)),
    high: Number(item.high.toFixed(2)),
    low: Number(item.low.toFixed(2)),
    close: Number(item.close.toFixed(2)),
    volume: item.volume
  }));
}

function useStrategyStockKline() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const requestIdRef = useRef(0);

  const loadKline = useCallback(async symbol => {
    if (!symbol) return;
    const requestId = ++requestIdRef.current;
    const cachedRows = historyCache.get(symbol);
    if (cachedRows) {
      setData({ dataSource: '本地历史行情', adjustLabel: '前复权', rows: cachedRows });
      return;
    }

    setLoading(true);
    setError('');
    try {
      const response = await getDailyBarsApi({
        symbol,
        start: moment().subtract(1, 'year').format('YYYY-MM-DD'),
        end: moment().format('YYYY-MM-DD')
      });
      const rows = transformHistory(response?.data);
      historyCache.set(symbol, rows);
      if (requestId === requestIdRef.current) {
        setData({ dataSource: '本地历史行情', adjustLabel: '前复权', rows });
      }
    } catch (requestError) {
      if (requestId === requestIdRef.current) {
        setError(requestError.message || 'K 线加载失败');
      }
    } finally {
      if (requestId === requestIdRef.current) setLoading(false);
    }
  }, []);

  useEffect(() => () => {
    requestIdRef.current += 1;
  }, []);

  return { data, loading, error, loadKline };
}

const columnDefs = [
  { headerName: '股票', field: 'name', minWidth: 120, flex: 1, cellStyle: { color: '#ff7f50', fontWeight: 700 } },
  { headerName: '代码', field: 'symbol', minWidth: 110, flex: 1 },
  { headerName: '信号阶段', field: 'signal_stage', minWidth: 96, flex: 0.7, valueFormatter: params => params.value || '-' },
  { headerName: '前高', field: 'first_peak', minWidth: 88, flex: 0.7, valueFormatter: params => formatNumber(params.value) },
  { headerName: '中间回落', field: 'pullback_depth', minWidth: 104, flex: 0.8, cellRenderer: PercentCell },
  { headerName: '上影占比', field: 'upper_wick_ratio', minWidth: 104, flex: 0.8, valueFormatter: params => formatPlainPercent(params.value) },
  { headerName: '阴线实体', field: 'bear_body_ratio', minWidth: 104, flex: 0.8, valueFormatter: params => formatPlainPercent(params.value) },
  { headerName: '突破涨幅', field: 'breakout_return', minWidth: 104, flex: 0.8, cellRenderer: PercentCell },
  { headerName: '回调量比', field: 'pullback_volume_ratio', minWidth: 104, flex: 0.8, valueFormatter: params => `${formatNumber(params.value)}x` },
  { headerName: '最新价', field: 'latest_close', minWidth: 88, flex: 0.7, valueFormatter: params => formatNumber(params.value) },
  { headerName: '今日涨幅', field: 'latest_1d_pct', minWidth: 104, flex: 0.8, cellRenderer: PercentCell },
  { headerName: '5日涨幅', field: 'latest_5d_pct', minWidth: 104, flex: 0.8, cellRenderer: PercentCell },
  { headerName: '成交量比', field: 'volume_ratio', minWidth: 104, flex: 0.8, valueFormatter: params => `${formatNumber(params.value)}x` },
  { headerName: '市值(亿)', field: 'market_cap', minWidth: 104, flex: 0.8, valueFormatter: params => formatMarketCap(params.value) },
  { headerName: '热度排名', field: 'hot_rank', minWidth: 100, flex: 0.7, valueFormatter: params => params.value ? `#${params.value}` : '-' }
];

function StrategyKlineRow({ data }) {
  const stock = data.stock;
  const [period, setPeriod] = useState('daily');
  const { data: klineData, loading, error, loadKline } = useStrategyStockKline();

  useEffect(() => {
    loadKline(stock.symbol);
  }, [loadKline, stock.symbol]);

  return (
    <div className={styles.klineRow}>
      <StockKlineChart
        stock={{ ...stock, code: stock.symbol }}
        data={klineData}
        loading={loading}
        error={error}
        period={period}
        onPeriodChange={setPeriod}
        enableMouseWheelZoom={false}
      />
    </div>
  );
}

function keepKlineRowsWithStocks({ nodes }) {
  const klineRowsByStock = new Map(
    nodes.filter(node => node.data?.rowType === 'kline').map(node => [node.data.parentRowId, node])
  );
  const stockRows = nodes.filter(node => node.data?.rowType !== 'kline');
  nodes.length = 0;
  stockRows.forEach(stockRow => {
    nodes.push(stockRow);
    const klineRow = klineRowsByStock.get(stockRow.data.rowId);
    if (klineRow) nodes.push(klineRow);
  });
}

export default function StrategyResultsTable({ rows, loading }) {
  const rowData = useMemo(
    () => rows.flatMap((row, index) => {
      const rowKey = `${row.symbol}-${index}`;
      const stockRowId = `stock-${rowKey}`;
      return [
        { ...row, rowId: stockRowId },
        { rowType: 'kline', rowId: `kline-${rowKey}`, parentRowId: stockRowId, stock: row }
      ];
    }),
    [rows]
  );

  return (
    <div className={styles.grid}>
      <AgGridProvider modules={modules}>
        <AgGridReact
          theme={themeDark}
          rowData={rowData}
          columnDefs={columnDefs}
          defaultColDef={{ resizable: true, sortable: true }}
          fullWidthCellRenderer={StrategyKlineRow}
          getRowHeight={params => (params.data?.rowType === 'kline' ? KLINE_ROW_HEIGHT : undefined)}
          getRowId={params => params.data.rowId}
          isFullWidthRow={params => params.rowNode.data?.rowType === 'kline'}
          loading={loading}
          overlayNoRowsTemplate="<span>当前策略暂无命中股票</span>"
          postSortRows={keepKlineRowsWithStocks}
          suppressCellFocus
        />
      </AgGridProvider>
    </div>
  );
}
