import request from './request.js';

// 获取行情快照
export const getPriceSnapshotApi = (thscodes) => {
  return request.get('/a-share/prices/snapshot', { thscodes });
};

// 获取股票飙升榜
export const getSkyRocketListApi = (period) => {
  return request.get('/a-share/special-data/skyrocket-list', { period });
};

// 获取股票热榜
export const getHotStockListApi = (period) => {
  return request.get('/a-share/special-data/hot-stock-list', { period });
};

