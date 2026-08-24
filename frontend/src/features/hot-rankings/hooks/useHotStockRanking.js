import { useCallback, useEffect, useRef, useState } from 'react';

import { getHotStockListApi } from '@/api/hithink/api.js';

const initialRanking = {
  title: '同花顺热榜',
  timestamp: null,
  rows: []
};

export function useHotStockRanking() {
  const [ranking, setRanking] = useState(initialRanking);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const requestIdRef = useRef(0);

  const loadRanking = useCallback(async () => {
    const requestId = ++requestIdRef.current;
    setLoading(true);
    setError('');

    try {
      const response = await getHotStockListApi('hour');
      if (requestId !== requestIdRef.current) return;

      setRanking({
        title: '同花顺热榜',
        timestamp: response?.data?.timestamp ?? null,
        rows: Array.isArray(response?.data?.item) ? response.data.item : []
      });
    } catch (requestError) {
      if (requestId !== requestIdRef.current) return;
      console.error('获取股票热榜失败', requestError);
      setError(requestError.message || '获取股票热榜失败');
    } finally {
      if (requestId === requestIdRef.current) setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadRanking();
    return () => {
      requestIdRef.current += 1;
    };
  }, [loadRanking]);

  return {
    ranking,
    loading,
    error,
    refresh: loadRanking
  };
}
