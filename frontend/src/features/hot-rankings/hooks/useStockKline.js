import { useCallback, useEffect, useRef, useState } from 'react';
import moment from 'moment';

import { getHistoricalPriceApi } from '@/api/hithink/api.js';
import { transformStockHistory } from '../utils/transformers.js';

export function useStockKline() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const requestIdRef = useRef(0);

  const loadKline = useCallback(async thscode => {
    if (!thscode) return;

    const requestId = ++requestIdRef.current;
    setLoading(true);
    setError('');

    try {
      const response = await getHistoricalPriceApi({
        thscode,
        interval: '1d',
        start: moment().subtract(1, 'year').valueOf(),
        end: moment().valueOf()
      });
      if (requestId !== requestIdRef.current) return;

      setData({
        dataSource: '同花顺 HiThink',
        adjustLabel: '前复权',
        rows: transformStockHistory(response?.data?.item)
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
