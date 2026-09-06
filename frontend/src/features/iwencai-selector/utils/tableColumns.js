import { preferredColumns } from '../constants.js';

export function collectColumns(rows, sampleSize = 100) {
  const keys = [];
  const seen = new Set();
  rows.slice(0, sampleSize).forEach(row => {
    Object.keys(row).forEach(key => {
      if (!seen.has(key)) {
        seen.add(key);
        keys.push(key);
      }
    });
  });
  return [...preferredColumns.filter(key => seen.has(key)), ...keys.filter(key => !preferredColumns.includes(key))];
}
