import moment from 'moment';

export function transformStockHistory(items = []) {
  if (!Array.isArray(items)) return [];

  return items.flatMap(item => {
    const date = moment(Number(item.date_ms));
    const open = Number(item.open_price);
    const high = Number(item.high_price);
    const low = Number(item.low_price);
    const close = Number(item.close_price);
    const volume = Number(item.volume);

    if (!date.isValid() || ![open, high, low, close, volume].every(Number.isFinite)) {
      return [];
    }

    return [
      {
        date: date.format('YYYY-MM-DD'),
        open: Number(open.toFixed(2)),
        high: Number(high.toFixed(2)),
        low: Number(low.toFixed(2)),
        close: Number(close.toFixed(2)),
        volume
      }
    ];
  });
}

export function transformHotRankingResponse(payload) {
  const normalizeRows = rows =>
    (Array.isArray(rows) ? rows : []).map((row, index) => ({
      ...row,
      rank: row.rank ?? index + 1,
      name: row.name ?? row.股票简称 ?? '',
      thscode: row.thscode ?? row.code ?? row.symbol ?? '',
      heat: row.heat ?? row.hot_value ?? row.hotRank ?? '-'
    }));

  if (Array.isArray(payload?.items)) {
    const ranking = payload.items.find(item => item.id === 'hot-stock-list') || payload.items[0];
    return {
      id: ranking?.id || 'hot-stock-list',
      title: ranking?.title || '同花顺热榜',
      timestamp: ranking?.timestamp || ranking?.updatedAt || null,
      rows: normalizeRows(ranking?.rows)
    };
  }

  return {
    id: 'hot-stock-list',
    title: '同花顺热榜',
    timestamp: payload?.data?.timestamp ?? null,
    rows: normalizeRows(payload?.data?.item)
  };
}
