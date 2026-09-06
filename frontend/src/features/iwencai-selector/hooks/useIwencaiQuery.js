import { useCallback, useEffect, useMemo, useState } from 'react';

import { getIwencaiStatus, runIwencaiQuery } from '../api/iwencaiApi.js';

const emptyRows = [];

export function useIwencaiQuery() {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState(null);
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const controller = new AbortController();
    async function loadStatus() {
      try {
        const payload = await getIwencaiStatus({ signal: controller.signal });
        setStatus(payload);
        if (payload.latest) {
          setResult(payload.latest);
          setQuery(payload.latest.query || '');
        }
      } catch (requestError) {
        if (requestError.name !== 'AbortError') setError(requestError.message);
      }
    }
    loadStatus();
    return () => controller.abort();
  }, []);

  const submitQuery = useCallback(async () => {
    const normalized = query.trim();
    if (!normalized || loading) return;
    setLoading(true);
    setError('');
    try {
      const payload = await runIwencaiQuery(normalized);
      setResult(payload.item);
      if (payload.item.query_rewritten) setQuery(payload.item.query);
      setStatus(current => ({ ...current, latest: payload.item }));
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }, [loading, query]);

  const rows = useMemo(() => result?.datas || emptyRows, [result]);
  const reportedCount = result?.code_count ?? rows.length;
  const queryStatus = status ? (status.configured ? '已配置' : '待配置') : error ? '后端未连接' : '连接中';
  const apiKeyBadge = status
    ? status.configured ? 'API Key 已配置' : 'API Key 未配置'
    : error ? '后端未连接' : '正在连接后端';

  return { query, setQuery, result, status, loading, error, rows, reportedCount, queryStatus, apiKeyBadge, submitQuery };
}
