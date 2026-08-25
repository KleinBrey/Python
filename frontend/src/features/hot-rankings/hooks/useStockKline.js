import { useCallback, useEffect, useRef, useState } from 'react';
import moment from 'moment';
import { getDailyBarsApi } from '@/api/quantide/api.js';
import { transformStockHistory } from '../utils/transformers.js';

const klineCache = new Map();
const pendingRequests = new Map();

export function useStockKline() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const requestIdRef = useRef(0);

  const loadKline = useCallback(async symbol => {
    if (!symbol) return;

    const requestId = ++requestIdRef.current;
    const cachedData = klineCache.get(symbol);

    if (cachedData) {
      setData(cachedData);
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
        }).then(response => ({
          dataSource: '同花顺 HiThink',
          adjustLabel: '前复权',
          rows: transformStockHistory(response?.data)
        }));
        pendingRequests.set(symbol, request);
      }

      const nextData = await request;
      klineCache.set(symbol, nextData);
      pendingRequests.delete(symbol);

      if (requestId !== requestIdRef.current) return;

      setData(nextData);
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

  useEffect(
    () => () => {
      requestIdRef.current += 1;
    },
    []
  );

  return {
    data,
    loading,
    error,
    loadKline
  };
}
