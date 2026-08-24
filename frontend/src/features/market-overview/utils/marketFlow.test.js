import assert from 'node:assert/strict';
import test from 'node:test';

import { formatFlow, summarizeMarketFlow } from './marketFlow.js';

test('formatFlow formats positive and negative values', () => {
  assert.equal(formatFlow(2), '+2.00');
  assert.equal(formatFlow(-2), '-2.00');
});

test('summarizeMarketFlow returns ranked and aggregated values', () => {
  const summary = summarizeMarketFlow([
    { name: 'A', end: 5 },
    { name: 'B', end: -2 },
    { name: 'C', end: 3 },
    { name: 'D', end: -8 }
  ]);

  assert.equal(summary.totalPositive, 8);
  assert.equal(summary.totalNegative, -10);
  assert.deepEqual(summary.leaders.map(item => item.name), ['A', 'C', 'B']);
  assert.deepEqual(summary.laggards.map(item => item.name), ['D', 'B', 'C']);
});
