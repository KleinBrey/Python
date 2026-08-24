import assert from 'node:assert/strict';
import test from 'node:test';

import { transformHotRankingResponse, transformStockHistory } from './transformers.js';

test('transformStockHistory normalizes valid rows and removes invalid rows', () => {
  const rows = transformStockHistory([
    { date_ms: 1704067200000, open_price: '10.126', high_price: 11, low_price: 9, close_price: 10.5, volume: '1000' },
    { date_ms: 'invalid', open_price: 1, high_price: 1, low_price: 1, close_price: 1, volume: 1 }
  ]);

  assert.equal(rows.length, 1);
  assert.equal(rows[0].open, 10.13);
  assert.equal(rows[0].volume, 1000);
});

test('transformHotRankingResponse supports and normalizes the backend ranking payload', () => {
  const result = transformHotRankingResponse({ items: [{ id: 'hot-stock-list', title: '热榜', updatedAt: 'now', rows: [{ symbol: '600519.SH', hot_value: 99 }] }] });
  assert.equal(result.title, '热榜');
  assert.equal(result.timestamp, 'now');
  assert.equal(result.rows.length, 1);
  assert.equal(result.rows[0].thscode, '600519.SH');
  assert.equal(result.rows[0].heat, 99);
});
