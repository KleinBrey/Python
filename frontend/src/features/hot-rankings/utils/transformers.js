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
