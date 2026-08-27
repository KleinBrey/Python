import request from '@/api/quantide/request.js';

export function syncStockList() {
  return request.post('/api/database-sync/stock-list', {}, { timeout: 0 });
}

export function syncDailyK() {
  return request.post('/api/database-sync/daily-k', {}, { timeout: 0 });
}

export function syncHotStock() {
  return request.post('/api/database-sync/hot-stock', {}, { timeout: 0 });
}
