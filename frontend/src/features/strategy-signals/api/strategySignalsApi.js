import { apiGet } from '@/api/client.js';

export function getStrategies({ signal } = {}) {
  return apiGet('/api/strategies', { signal });
}

export function getStrategySignals(strategyId, { limit = 100, signal } = {}) {
  return apiGet(`/api/strategies/${encodeURIComponent(strategyId)}/signals?limit=${limit}`, { signal });
}
