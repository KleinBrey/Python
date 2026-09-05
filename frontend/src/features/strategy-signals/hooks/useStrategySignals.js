import { useCallback, useEffect, useRef, useState } from 'react';

import { getStrategies, getStrategySignals } from '../api/strategySignalsApi.js';

export function useStrategySignals() {
  const [strategies, setStrategies] = useState([]);
  const [activeStrategyId, setActiveStrategyId] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const requestIdRef = useRef(0);
  const signalRequestControllerRef = useRef(null);

  const loadSignals = useCallback(async strategyId => {
    signalRequestControllerRef.current?.abort();

    const controller = new AbortController();
    signalRequestControllerRef.current = controller;
    const requestId = ++requestIdRef.current;
    setLoading(true);
    setError('');
    try {
      const payload = await getStrategySignals(strategyId, { signal: controller.signal });
      if (requestId === requestIdRef.current) setResult(payload);
    } catch (requestError) {
      if (requestError.name !== 'AbortError' && requestId === requestIdRef.current) {
        setError(requestError.message || '策略结果加载失败');
      }
    } finally {
      if (signalRequestControllerRef.current === controller) {
        signalRequestControllerRef.current = null;
        if (!controller.signal.aborted && requestId === requestIdRef.current) {
          setLoading(false);
        }
      }
    }
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    async function initialize() {
      try {
        const payload = await getStrategies({ signal: controller.signal });
        const strategyItems = Array.isArray(payload?.items) ? payload.items : [];
        const firstStrategyId = strategyItems[0]?.id || '';
        setStrategies(strategyItems);
        setActiveStrategyId(firstStrategyId);
        if (firstStrategyId) {
          await loadSignals(firstStrategyId);
        } else {
          setLoading(false);
        }
      } catch (requestError) {
        if (requestError.name !== 'AbortError') {
          setError(requestError.message || '策略列表加载失败');
          setLoading(false);
        }
      }
    }

    initialize();
    return () => {
      controller.abort();
      signalRequestControllerRef.current?.abort();
      signalRequestControllerRef.current = null;
      requestIdRef.current += 1;
    };
  }, [loadSignals]);

  const selectStrategy = useCallback(
    strategyId => {
      if (!strategyId || strategyId === activeStrategyId) return;
      setActiveStrategyId(strategyId);
      setResult(null);
      loadSignals(strategyId);
    },
    [activeStrategyId, loadSignals]
  );

  return {
    strategies,
    activeStrategyId,
    result,
    loading,
    error,
    selectStrategy,
    refresh: () => activeStrategyId && loadSignals(activeStrategyId)
  };
}
