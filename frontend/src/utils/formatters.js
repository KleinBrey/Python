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
    degraded: '部分可用',
    missing: '未配置',
    error: '读取失败',
    offline: '不可用',
    blocked: '待配置',
    idle: '待执行',
    running: '执行中',
    success: '已完成',
    failed: '执行失败',
  };
  return labels[status] || fallback;
}

export function statusTone(status) {
  if (status === 'online' || status === 'ready' || status === 'success') return 'ok';
  if (status === 'blocked' || status === 'degraded' || status === 'missing' || status === 'running') return 'warn';
  if (status === 'offline' || status === 'error' || status === 'failed') return 'bad';
  return 'idle';
}
