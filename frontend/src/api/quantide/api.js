import request from './request.js';

// 获取股票标的列表
export function getStocksListApi(params = {}) {
  return request.get('/api/stocks-list', params);
}

// 更新股票标的列表
export function updateStocksListApi(params = {}) {
  return request.post('/api/stocks-list', params);
}
