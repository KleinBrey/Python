import request from './request.js';

// 获取股票标的列表
export function getStocksListApi(params = {}) {
  return request.get('/api/stocks-list', params);
}

// 更新股票标的列表
export function updateStocksListApi(params = {}) {
  return request.post('/api/stocks-list', params);
}

// 获取指定股票在日期范围内的日 K 线
export function getDailyBarsApi(params = {}) {
  return request.get('/api/daily-bars', params);
}

// 获取指定股票在日期范围内的日 K 线
export function getHotStocksApi(params = {}) {
  return request.get('/api/hot-stock', params);
}
