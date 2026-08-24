import assert from 'node:assert/strict';
import test from 'node:test';

import { buildDatabaseViewModel } from './databaseViewModel.js';

test('buildDatabaseViewModel summarizes collections and selects a preview', () => {
  const result = buildDatabaseViewModel({
    collections: [
      { id: 'empty', count: 2, preview: [] },
      { id: 'stocks', count: '3', preview: [{ symbol: '600519', name: '贵州茅台' }] }
    ]
  });

  assert.equal(result.totalRows, 5);
  assert.equal(result.previewCollection.id, 'stocks');
  assert.deepEqual(result.previewColumns, ['symbol', 'name']);
});

test('buildDatabaseViewModel handles an empty response', () => {
  assert.deepEqual(buildDatabaseViewModel(null), {
    collections: [],
    totalRows: 0,
    previewCollection: undefined,
    previewRows: [],
    previewColumns: []
  });
});
