import { useEffect, useState } from 'react';

import { getStockHistory, prefetchStockHistories } from '../api/iwencaiApi.js';

export function useIwencaiMarketData(rows, status) {
  const [selectedStock, setSelectedStock] = useState(null);
  const [klineData, setKlineData] = useState(null);
  const [klineLoading, setKlineLoading] = useState(false);
  const [klineError, setKlineError] = useState('');
  const [klinePeriod, setKlinePeriod] = useState('daily');
  const [prefetchStatus, setPrefetchStatus] = useState(null);

  useEffect(() => {
    if (!rows.length) {
      setSelectedStock(null);
      return;
    }
    setSelectedStock(current =>
      current && rows.some(row => row.股票代码 === current.股票代码) ? current : rows[0]
    );
  }, [rows]);

  useEffect(() => {
    if (!rows.length) {
      setPrefetchStatus(null);
      return undefined;
    }
    if (status?.marketDataConfigured === false) {
      setPrefetchStatus({ state: 'warning', message: '未配置 HiThink API Key，暂不预缓存日线' });
      return undefined;
    }

    const controller = new AbortController();
    const stocks = rows.slice(0, 300).map(row => ({ symbol: row.股票代码, name: row.股票简称 }));
    async function prefetch() {
      setPrefetchStatus({ state: 'loading', message: `正在预缓存 ${stocks.length} 只股票日线` });
      try {
        const payload = await prefetchStockHistories(stocks, { signal: controller.signal });
        const summary = payload.item;
        setPrefetchStatus({
          state: summary.failed ? 'warning' : 'success',
          message: summary.failed
            ? `已缓存 ${summary.completed} 只，${summary.failed} 只失败`
            : `已缓存 ${summary.completed} 只股票日线，点击即可显示`
        });
      } catch (requestError) {
        if (requestError.name !== 'AbortError') {
          setPrefetchStatus({ state: 'warning', message: `日线预缓存失败：${requestError.message}` });
        }
      }
    }
    prefetch();
    return () => controller.abort();
  }, [rows, status?.marketDataConfigured]);

  useEffect(() => {
    const controller = new AbortController();
    async function loadKline() {
      if (!selectedStock?.股票代码) return;
      if (status?.marketDataConfigured === false) {
        setKlineData(null);
        setKlineLoading(false);
        setKlineError('未配置 HITHINK_FINANCE_API_KEY，无法读取 HiThink 历史行情');
        return;
      }
      setKlineLoading(true);
      setKlineError('');
      try {
        const payload = await getStockHistory({ stock: selectedStock, period: klinePeriod, signal: controller.signal });
        setKlineData(payload.item);
      } catch (requestError) {
        if (requestError.name !== 'AbortError') {
          setKlineData(null);
          setKlineError(requestError.message);
        }
      } finally {
        if (!controller.signal.aborted) setKlineLoading(false);
      }
    }
    loadKline();
    return () => controller.abort();
  }, [selectedStock, klinePeriod, status?.marketDataConfigured]);

  return { selectedStock, setSelectedStock, klineData, klineLoading, klineError, klinePeriod, setKlinePeriod, prefetchStatus };
}
