import { apiGet, apiPost } from '@/api/client.js';

export function getIwencaiStatus({ signal } = {}) {
  return apiGet('/api/iwencai/status', { signal });
}

export function runIwencaiQuery(query, { signal } = {}) {
  return apiPost('/api/iwencai/query', { query, pageSize: 50, maxPages: 100, timeout: 60 }, { signal });
}

export function prefetchStockHistories(stocks, { signal } = {}) {
  return apiPost('/api/stocks/history/prefetch', { stocks, adjust: 'none', workers: 4 }, { signal });
}

export function getStockHistory({ stock, period, signal }) {
  const symbol = String(stock?.股票代码 || '').replace(/\.(SZ|SH|BJ)$/i, '');
  const name = String(stock?.股票简称 || '');
  const params = new URLSearchParams({ symbol, name, period });
  return apiGet(`/api/stocks/history?${params.toString()}`, { signal });
}
