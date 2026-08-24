import { useCallback, useEffect, useRef, useState } from 'react';
import moment from 'moment';
import { getDailyBarsApi } from '@/api/quantide/api.js';
import { transformStockHistory } from '../utils/transformers.js';

export function useStockKline() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const requestIdRef = useRef(0);

  const loadKline = useCallback(async symbol => {
    if (!symbol) return;

    const requestId = ++requestIdRef.current;

    setLoading(true);

    setError('');

    try {
      const response = await getDailyBarsApi({
        symbol,
        start_date: moment().subtract(1, 'year').format('YYYY-MM-DD'),
        end_date: moment().format('YYYY-MM-DD')
      });

      if (requestId !== requestIdRef.current) return;

      setData({
        dataSource: '同花顺 HiThink',
        adjustLabel: '前复权',
        rows: transformStockHistory(response?.data)
      });
    } catch (requestError) {
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
