import { useCallback, useEffect, useRef, useState } from 'react';
import moment from 'moment';
import { getDailyBarsApi } from '@/api/quantide/api.js';
import { mergeAShareStockHistoryWithSnapshot, transformAShareStockHistory } from '../utils/aShareMarketTransformers.js';
import { useTradingCalendar } from '@/contexts';

const historyCache = new Map();
const pendingRequests = new Map();

export function useAShareStockKline() {
  const { getLatestTradingDay } = useTradingCalendar();

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const requestIdRef = useRef(0);

  const loadKline = useCallback(async (symbol, todaySnapshot) => {
    if (!symbol) return;

    const latestTradingDay = moment(await getLatestTradingDay()).format('YYYY-MM-DD');

    const requestId = ++requestIdRef.current;
    const cachedRows = historyCache.get(symbol);

    if (cachedRows) {
      setData({
        dataSource: '本地历史 + 同花顺快照',
        adjustLabel: '前复权',
        rows: mergeAShareStockHistoryWithSnapshot(cachedRows, todaySnapshot)
      });
      setError('');
      setLoading(false);
      return;
    }

    setLoading(true);
    setData(null);
    setError('');

    try {
      let request = pendingRequests.get(symbol);

      if (!request) {
        request = getDailyBarsApi({
          symbol,
          start: moment().subtract(1, 'year').format('YYYY-MM-DD'),
          end: moment().format('YYYY-MM-DD')
        }).then(response => transformAShareStockHistory(response?.data));
        pendingRequests.set(symbol, request);
      }

      const historyRows = await request;
      historyCache.set(symbol, historyRows);
      pendingRequests.delete(symbol);

      if (requestId !== requestIdRef.current) return;

      const latestDatabaseTradingDay = historyRows.at(-1).date;

      if (latestDatabaseTradingDay === latestTradingDay) {
        setData({
          dataSource: '本地历史 + 同花顺快照',
          adjustLabel: '前复权',
          rows: historyRows
        });
      } else {
        setData({
          dataSource: '本地历史 + 同花顺快照',
          adjustLabel: '前复权',
          rows: mergeAShareStockHistoryWithSnapshot(historyRows, todaySnapshot)
        });
      }
    } catch (requestError) {
      pendingRequests.delete(symbol);
      if (requestId !== requestIdRef.current) return;
      console.error('K 线加载失败', requestError);
      setData(null);
      setError(requestError.message || 'K 线加载失败');
    } finally {
      if (requestId === requestIdRef.current) setLoading(false);
    }
  }, []);

  useEffect(() => {
    // 清理函数
    return () => {
      requestIdRef.current += 1;
    };
  }, []);

  return {
    data,
    loading,
    error,
    loadKline
  };
}
