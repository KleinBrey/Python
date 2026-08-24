import assert from 'node:assert/strict';
import test from 'node:test';

import { collectColumns } from './tableColumns.js';

test('collectColumns puts preferred stock columns first without duplicates', () => {
  const columns = collectColumns([
    { 自定义指标: 1, 股票简称: '平安银行', 股票代码: '000001' },
    { 最新价: 10, 自定义指标: 2 }
  ]);

  assert.deepEqual(columns, ['股票代码', '股票简称', '最新价', '自定义指标']);
});

test('collectColumns respects the sample size', () => {
  assert.deepEqual(collectColumns([{ a: 1 }, { b: 2 }], 1), ['a']);
});
