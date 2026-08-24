import { useCallback, useEffect, useState } from 'react';

import { getDatabaseStatus } from '../api/databaseApi.js';

export function useDatabaseStatus() {
  const [databaseStatus, setDatabaseStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const refresh = useCallback(async signal => {
    setLoading(true);
    setError('');
    try {
      setDatabaseStatus(await getDatabaseStatus({ signal }));
    } catch (requestError) {
      if (requestError.name !== 'AbortError') setError(requestError.message);
    } finally {
      if (!signal?.aborted) setLoading(false);
    }
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    refresh(controller.signal);
    return () => controller.abort();
  }, [refresh]);

  return { databaseStatus, loading, error, refresh };
}
