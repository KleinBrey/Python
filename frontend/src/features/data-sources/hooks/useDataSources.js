import { useCallback, useEffect, useState } from 'react';

import { getDataSources } from '../api/dataSourcesApi.js';

export function useDataSources() {
  const [dataSources, setDataSources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadDataSources = useCallback(async (check = false, signal) => {
    setLoading(true);
    setError('');
    try {
      const payload = await getDataSources({ check, signal });
      setDataSources(payload.items || []);
    } catch (requestError) {
      if (requestError.name !== 'AbortError') setError(requestError.message);
    } finally {
      if (!signal?.aborted) setLoading(false);
    }
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    loadDataSources(false, controller.signal);
    return () => controller.abort();
  }, [loadDataSources]);

  return {
    dataSources,
    loading,
    error,
    checkConnection: () => loadDataSources(true)
  };
}
