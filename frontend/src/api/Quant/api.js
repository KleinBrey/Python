import request from './request.js'



/**
 * 获取标的列表
 */
export function getStocksListApi(params = {}) {
  return request.get('/api/stocks-list', params)
}

export function updateStocksListApi(params = {}) {
  return request.post('/api/stocks-list', params)
}

