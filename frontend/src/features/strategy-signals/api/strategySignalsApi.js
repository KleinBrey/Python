import { apiGet } from '@/api/client.js';

export function getStrategyStocks({ source = 'all', limit = 1000, signal } = {}) {
  return apiGet(`/api/strategy-stocks?source=${encodeURIComponent(source)}&limit=${limit}`, { signal });
}
