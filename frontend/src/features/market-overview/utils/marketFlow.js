import { marketFlowSeries, timeLabels } from '../data/marketFlowData.js';

export function formatFlow(value) {
  const sign = value > 0 ? '+' : '';
  return `${sign}${value.toFixed(2)}`;
}

export function summarizeMarketFlow(series = marketFlowSeries) {
  const sorted = [...series].sort((left, right) => right.end - left.end);
  return {
    leaders: sorted.slice(0, 3),
    laggards: sorted.slice(-3).reverse(),
    totalPositive: series.filter(item => item.end > 0).reduce((sum, item) => sum + item.end, 0),
    totalNegative: series.filter(item => item.end < 0).reduce((sum, item) => sum + item.end, 0)
  };
}

function buildMarkLine(series, visibleCount) {
  const currentIndex = Math.max(0, Math.min(visibleCount - 1, timeLabels.length - 1));
  const currentValue = series.points[currentIndex] ?? series.end;
  const labelStartIndex = Math.max(0, currentIndex - 5);
  return {
    silent: true, symbol: ['none', 'circle'], symbolSize: 5,
    lineStyle: { color: series.color, opacity: 0.5, width: 1, type: 'dashed' },
    label: { show: true, position: 'end', distance: 7, color: '#e5e7eb', backgroundColor: '#18181b', borderColor: series.color, borderWidth: 1, borderRadius: 5, padding: [3, 5], formatter: `${series.name} ${formatFlow(currentValue)}`, fontSize: 11, fontWeight: 700 },
    data: [[{ coord: [labelStartIndex, currentValue] }, { coord: [currentIndex, currentValue] }]]
  };
}

export function buildMarketFlowOption(visibleCount = timeLabels.length) {
  const boundedVisibleCount = Math.max(1, Math.min(visibleCount, timeLabels.length));
  return {
    backgroundColor: 'transparent', animationDuration: 260, animationDurationUpdate: 90,
    color: marketFlowSeries.map(item => item.color),
    grid: { left: 54, right: 150, top: 34, bottom: 50 },
    tooltip: { trigger: 'axis', backgroundColor: '#18181b', borderColor: '#3f3f46', textStyle: { color: '#f8fafc' }, valueFormatter: value => `${Number(value).toFixed(2)} 亿` },
    legend: { type: 'scroll', bottom: 6, left: 42, right: 42, itemWidth: 10, itemHeight: 10, textStyle: { color: '#a1a1aa', fontSize: 12 }, pageIconColor: '#a1a1aa', pageTextStyle: { color: '#a1a1aa' } },
    xAxis: { type: 'category', boundaryGap: false, data: timeLabels, axisLine: { lineStyle: { color: '#3f3f46' } }, axisTick: { show: false }, axisLabel: { color: '#a1a1aa', interval: (index, label) => ['09:30', '10:30', '11:30', '14:00', '15:00'].includes(label), fontWeight: 700 }, splitLine: { show: true, interval: (index, label) => label === '11:30', lineStyle: { color: '#27272a', type: 'dashed' } } },
    yAxis: { type: 'value', min: -120, max: 120, interval: 30, axisLabel: { color: '#a1a1aa', formatter: value => `${value}亿`, fontWeight: 700 }, axisLine: { show: false }, axisTick: { show: false }, splitLine: { lineStyle: { color: '#27272a' } } },
    series: marketFlowSeries.map(item => ({ name: item.name, type: 'line', data: item.points.slice(0, boundedVisibleCount), smooth: true, showSymbol: false, symbolSize: 5, lineStyle: { width: Math.abs(item.end) > 70 ? 3 : 2, color: item.color }, emphasis: { focus: 'series', lineStyle: { width: 4 } }, endLabel: { show: false }, markLine: buildMarkLine(item, boundedVisibleCount) }))
  };
}
