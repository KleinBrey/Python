export function formatValue(value) {
  if (value === null || value === undefined || value === '') return '-';
  const number = Number(value);
  if (Number.isFinite(number)) {
    return number.toLocaleString('zh-CN', { maximumFractionDigits: 2 });
  }
  return String(value);
}

export function shortTime(value) {
  if (!value) return '未刷新';
  return value.replace('T', ' ');
}

export function rankingScore(row) {
  return row.heat ?? row.change ?? row.price ?? '-';
}

export function latestRefreshTime(rankings) {
  const latest = rankings
    .map((ranking) => ranking.updatedAt)
    .filter(Boolean)
    .sort()
    .at(-1);
  return shortTime(latest);
}

export function trendClass(value) {
  const number = Number(value);
  if (!Number.isFinite(number) || number === 0) return '';
  return number > 0 ? 'up' : 'down';
}

export function statusLabel(status, fallback = '未知') {
  const labels = {
    online: '可连接',
    ready: '已就绪',
    offline: '不可用',
    blocked: '待配置',
  };
  return labels[status] || fallback;
}

export function statusTone(status) {
  if (status === 'online' || status === 'ready') return 'ok';
  if (status === 'blocked') return 'warn';
  if (status === 'offline') return 'bad';
  return 'idle';
}
