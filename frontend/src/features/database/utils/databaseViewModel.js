export function buildDatabaseViewModel(databaseStatus) {
  const collections = databaseStatus?.collections || [];
  const totalRows = collections.reduce((sum, item) => sum + (Number(item.count) || 0), 0);
  const previewCollection = collections.find(item => item.preview?.length) || collections[0];
  const previewRows = previewCollection?.preview || [];
  const previewColumns = [...new Set(previewRows.flatMap(row => Object.keys(row || {})))].slice(0, 6);

  return { collections, totalRows, previewCollection, previewRows, previewColumns };
}
