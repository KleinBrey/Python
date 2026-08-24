import { useCallback, useEffect, useMemo, useState } from 'react';

import { getStrategyStocks } from '../api/strategySignalsApi.js';

export function useStrategySignals() {
  const [sources, setSources] = useState([]);
  const [stocks, setStocks] = useState([]);
  const [activeSource, setActiveSource] = useState('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadStocks = useCallback(async (sourceId, signal) => {
    setLoading(true);
    setError('');
    try {
      const payload = await getStrategyStocks({ source: sourceId, signal });
      setSources(payload.sources || []);
      setStocks(payload.items || []);
    } catch (requestError) {
      if (requestError.name !== 'AbortError') setError(requestError.message);
    } finally {
      if (!signal?.aborted) setLoading(false);
    }
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    loadStocks('all', controller.signal);
    return () => controller.abort();
  }, [loadStocks]);

  const selectSource = useCallback(
    sourceId => {
      setActiveSource(sourceId);
      loadStocks(sourceId);
    },
    [loadStocks]
  );

  const sourceCountById = useMemo(
    () => Object.fromEntries(sources.map(source => [source.id, source.stockCount || 0])),
    [sources]
  );

  return {
    sources,
    stocks,
    activeSource,
    sourceCountById,
    loading,
    error,
    selectSource,
    refresh: () => loadStocks(activeSource)
  };
}
