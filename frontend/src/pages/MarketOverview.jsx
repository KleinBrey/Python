import React, { useEffect, useMemo, useRef, useState } from 'react';
import * as echarts from 'echarts/core';
import { LineChart } from 'echarts/charts';
import { GridComponent, LegendComponent, MarkLineComponent, TooltipComponent } from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import { BarChart3, ChartCandlestick, Clock3, Play, RotateCcw, TrendingDown, TrendingUp } from 'lucide-react';

echarts.use([CanvasRenderer, GridComponent, LegendComponent, LineChart, MarkLineComponent, TooltipComponent]);

const timeLabels = [
  '09:30', '09:35', '09:40', '09:45', '09:50', '09:55',
  '10:00', '10:05', '10:10', '10:15', '10:20', '10:25',
  '10:30', '10:35', '10:40', '10:45', '10:50', '10:55',
  '11:00', '11:05', '11:10', '11:15', '11:20', '11:25', '11:30',
  '13:00', '13:05', '13:10', '13:15', '13:20', '13:25', '13:30',
  '13:35', '13:40', '13:45', '13:50', '13:55', '14:00', '14:05',
  '14:10', '14:15', '14:20', '14:25', '14:30', '14:35', '14:40',
  '14:45', '14:50', '14:55', '15:00',
];

const marketFlowSeries = [
  { name: 'PCB', color: '#b91c1c', end: 88.75, points: [0, 12, 28, 43, 35, 46, 38, 22, 30, 18, 26, 41, 55, 66, 59, 57, 62, 58, 70, 76, 82, 88, 90, 89, 88, 88, 88, 87, 88, 89, 88, 88, 88, 88, 89, 88, 89, 88, 88, 88, 88, 88, 88, 88, 88, 89, 88, 89, 88, 88.75] },
  { name: '证券', color: '#c87935', end: 37.94, points: [0, 8, 24, 44, 35, 39, 31, 24, 22, 26, 19, 15, 17, 18, 20, 19, 20, 22, 23, 25, 26, 28, 30, 31, 32, 32, 33, 34, 34, 35, 35, 36, 36, 37, 37, 37, 38, 38, 38, 37, 38, 38, 38, 38, 38, 37, 38, 38, 38, 37.94] },
  { name: '军工', color: '#d97706', end: 34.88, points: [0, 5, 22, 28, 24, 18, 26, 21, 16, 14, 10, 13, 15, 16, 15, 17, 18, 18, 19, 20, 21, 23, 25, 26, 27, 27, 28, 28, 29, 30, 30, 31, 31, 32, 32, 33, 33, 34, 34, 34, 34, 35, 35, 35, 35, 34, 35, 35, 35, 34.88] },
  { name: 'MLCC', color: '#ef4444', end: 32.09, points: [0, -8, 16, 36, 28, 34, 26, 12, -8, -18, -26, -32, -38, -42, -40, -36, -31, -22, -18, -8, -2, 4, 11, 18, 24, 24, 25, 26, 27, 28, 28, 29, 30, 30, 31, 31, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32.09] },
  { name: '玻璃基板', color: '#64748b', end: 10.2, points: [0, -5, 2, 15, 12, 9, 8, 6, 4, 3, 2, 1, 2, 3, 3, 4, 5, 4, 4, 5, 6, 7, 8, 8, 9, 8, 9, 9, 9, 10, 10, 10, 10, 10, 10, 11, 10, 10, 11, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10.2] },
  { name: '白酒', color: '#38bdf8', end: 4.16, points: [0, 4, 10, 15, 12, 8, 4, 2, -1, -2, -1, 0, 1, 1, 2, 3, 3, 2, 2, 3, 4, 4, 5, 4, 5, 4, 5, 4, 4, 4, 4, 4, 5, 4, 4, 4, 5, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4.16] },
  { name: '稀土', color: '#0f766e', end: -1.72, points: [0, -8, -4, 8, 2, -1, -3, -5, -7, -8, -10, -12, -14, -15, -14, -12, -10, -9, -8, -7, -6, -5, -4, -4, -3, -4, -4, -3, -3, -2, -2, -2, -2, -2, -1, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -1.72] },
  { name: 'AI应用', color: '#166534', end: -10.43, points: [0, -12, -18, -25, -20, -17, -22, -24, -26, -29, -31, -33, -35, -36, -34, -32, -31, -29, -28, -27, -26, -24, -22, -20, -18, -17, -16, -15, -14, -14, -13, -13, -12, -12, -11, -11, -11, -10, -10, -10, -10, -10, -10, -10, -10, -10, -10, -10, -10, -10.43] },
  { name: '电网设备', color: '#14532d', end: -15.36, points: [0, -9, -13, -18, -20, -22, -21, -24, -28, -30, -32, -35, -38, -40, -42, -41, -39, -37, -35, -33, -31, -29, -27, -25, -23, -23, -22, -21, -20, -19, -19, -18, -18, -17, -17, -16, -16, -16, -16, -15, -15, -15, -15, -15, -15, -15, -15, -15, -15, -15.36] },
  { name: '化工', color: '#2f855a', end: -23.28, points: [0, -10, -21, -29, -32, -35, -34, -36, -38, -40, -42, -45, -48, -50, -52, -51, -49, -47, -45, -43, -40, -37, -35, -33, -31, -30, -29, -28, -27, -26, -26, -25, -25, -24, -24, -24, -23, -23, -23, -23, -23, -23, -23, -23, -23, -23, -23, -23, -23, -23.28] },
  { name: '人形机器人', color: '#6b7280', end: -34.8, points: [0, 3, 10, 16, 12, 5, -2, -8, -10, -14, -18, -21, -24, -27, -30, -33, -35, -38, -41, -43, -45, -44, -42, -40, -38, -38, -37, -37, -36, -36, -36, -35, -35, -35, -35, -35, -35, -35, -35, -35, -35, -35, -35, -35, -35, -35, -35, -35, -35, -34.8] },
  { name: '锂矿', color: '#15803d', end: -41.66, points: [0, -16, -28, -38, -44, -48, -46, -43, -40, -39, -42, -45, -47, -48, -50, -52, -51, -49, -48, -47, -46, -45, -44, -43, -42, -42, -42, -42, -42, -42, -42, -42, -42, -42, -42, -42, -42, -42, -42, -42, -42, -42, -42, -42, -42, -42, -42, -42, -42, -41.66] },
  { name: '有色金属', color: '#166534', end: -51.5, points: [0, -18, -31, -44, -55, -62, -66, -67, -64, -61, -58, -55, -52, -50, -48, -47, -49, -51, -54, -56, -58, -59, -58, -56, -55, -55, -55, -54, -54, -53, -53, -52, -52, -52, -52, -52, -52, -52, -52, -52, -52, -52, -52, -52, -52, -51, -52, -52, -52, -51.5] },
  { name: '储能', color: '#14532d', end: -73.49, points: [0, -10, -24, -36, -47, -56, -62, -67, -70, -72, -75, -78, -80, -82, -84, -86, -88, -90, -91, -92, -91, -89, -87, -85, -83, -82, -80, -79, -78, -77, -76, -76, -75, -75, -74, -74, -74, -74, -73, -73, -73, -73, -73, -73, -73, -73, -73, -73, -73, -73.49] },
  { name: '电力设备', color: '#064e3b', end: -89.64, points: [0, -20, -31, -43, -55, -67, -72, -78, -84, -90, -96, -102, -108, -111, -112, -110, -107, -103, -99, -96, -94, -92, -91, -90, -89, -90, -91, -91, -91, -90, -90, -90, -90, -90, -90, -90, -90, -90, -90, -90, -90, -90, -90, -90, -90, -90, -90, -90, -90, -89.64] },
];

function formatFlow(value) {
  const sign = value > 0 ? '+' : '';
  return `${sign}${value.toFixed(2)}`;
}

function buildMarkLine(series, visibleCount) {
  const currentIndex = Math.max(0, Math.min(visibleCount - 1, timeLabels.length - 1));
  const currentValue = series.points[currentIndex] ?? series.end;
  const labelStartIndex = Math.max(0, currentIndex - 5);

  return {
    silent: true,
    symbol: ['none', 'circle'],
    symbolSize: 5,
    lineStyle: {
      color: series.color,
      opacity: 0.5,
      width: 1,
      type: 'dashed',
    },
    label: {
      show: true,
      position: 'end',
      distance: 7,
      color: '#e5e7eb',
      backgroundColor: '#18181b',
      borderColor: series.color,
      borderWidth: 1,
      borderRadius: 5,
      padding: [3, 5],
      formatter: `${series.name} ${formatFlow(currentValue)}`,
      fontSize: 11,
      fontWeight: 700,
    },
    data: [
      [
        { coord: [labelStartIndex, currentValue] },
        { coord: [currentIndex, currentValue] },
      ],
    ],
  };
}

function buildOption(visibleCount = timeLabels.length) {
  const boundedVisibleCount = Math.max(1, Math.min(visibleCount, timeLabels.length));

  return {
    backgroundColor: 'transparent',
    animationDuration: 260,
    animationDurationUpdate: 90,
    color: marketFlowSeries.map((item) => item.color),
    grid: {
      left: 54,
      right: 150,
      top: 34,
      bottom: 50,
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#18181b',
      borderColor: '#3f3f46',
      textStyle: { color: '#f8fafc' },
      valueFormatter: (value) => `${Number(value).toFixed(2)} 亿`,
    },
    legend: {
      type: 'scroll',
      bottom: 6,
      left: 42,
      right: 42,
      itemWidth: 10,
      itemHeight: 10,
      textStyle: { color: '#a1a1aa', fontSize: 12 },
      pageIconColor: '#a1a1aa',
      pageTextStyle: { color: '#a1a1aa' },
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: timeLabels,
      axisLine: { lineStyle: { color: '#3f3f46' } },
      axisTick: { show: false },
      axisLabel: {
        color: '#a1a1aa',
        interval: (index, label) => ['09:30', '10:30', '11:30', '14:00', '15:00'].includes(label),
        fontWeight: 700,
      },
      splitLine: {
        show: true,
        interval: (index, label) => ['11:30'].includes(label),
        lineStyle: { color: '#27272a', type: 'dashed' },
      },
    },
    yAxis: {
      type: 'value',
      min: -120,
      max: 120,
      interval: 30,
      axisLabel: {
        color: '#a1a1aa',
        formatter: (value) => `${value}亿`,
        fontWeight: 700,
      },
      axisLine: { show: false },
      axisTick: { show: false },
      splitLine: { lineStyle: { color: '#27272a' } },
    },
    series: marketFlowSeries.map((item) => ({
      name: item.name,
      type: 'line',
      data: item.points.slice(0, boundedVisibleCount),
      smooth: true,
      showSymbol: false,
      symbolSize: 5,
      lineStyle: {
        width: Math.abs(item.end) > 70 ? 3 : 2,
        color: item.color,
      },
      emphasis: {
        focus: 'series',
        lineStyle: { width: 4 },
      },
      endLabel: {
        show: false,
      },
      markLine: buildMarkLine(item, boundedVisibleCount),
    })),
  };
}

export default function MarketOverview() {
  const chartRef = useRef(null);
  const chartInstanceRef = useRef(null);
  const replayTimerRef = useRef(null);
  const [isReplaying, setIsReplaying] = useState(false);
  const [displayTime, setDisplayTime] = useState(timeLabels.at(-1));
  const sorted = useMemo(
    () => [...marketFlowSeries].sort((a, b) => b.end - a.end),
    [],
  );
  const leaders = sorted.slice(0, 3);
  const laggards = sorted.slice(-3).reverse();
  const totalPositive = marketFlowSeries
    .filter((item) => item.end > 0)
    .reduce((sum, item) => sum + item.end, 0);
  const totalNegative = marketFlowSeries
    .filter((item) => item.end < 0)
    .reduce((sum, item) => sum + item.end, 0);

  useEffect(() => {
    if (!chartRef.current) return undefined;

    const chart = echarts.init(chartRef.current);
    chartInstanceRef.current = chart;
    chart.setOption(buildOption());

    const handleResize = () => chart.resize();
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (replayTimerRef.current) {
        window.clearInterval(replayTimerRef.current);
      }
      chart.dispose();
    };
  }, []);

  function replayMarketFlow() {
    const chart = chartInstanceRef.current;
    if (!chart) return;

    if (replayTimerRef.current) {
      window.clearInterval(replayTimerRef.current);
    }

    let visibleCount = 1;
    setIsReplaying(true);
    setDisplayTime(timeLabels[0]);
    chart.setOption(buildOption(visibleCount), true);

    replayTimerRef.current = window.setInterval(() => {
      visibleCount += 1;
      const currentIndex = Math.min(visibleCount - 1, timeLabels.length - 1);
      setDisplayTime(timeLabels[currentIndex]);
      chart.setOption(buildOption(visibleCount), true);

      if (visibleCount >= timeLabels.length) {
        window.clearInterval(replayTimerRef.current);
        replayTimerRef.current = null;
        setIsReplaying(false);
      }
    }, 95);
  }

  return (
    <div className="dashboard-content market-overview">
      <section className="metric-grid" aria-label="市场概览">
        <article className="metric-card market-hero-card">
          <div className="metric-head">
            <span>收盘资金流向</span>
            <div className="metric-icon teal">
              <Clock3 size={17} />
            </div>
          </div>
          <strong>{displayTime}</strong>
          <p>{isReplaying ? '正在回放分时资金曲线' : 'Mock 分时数据，后续可替换为真实板块资金流'}</p>
        </article>
        <article className="metric-card">
          <div className="metric-head">
            <span>净流入合计</span>
            <div className="metric-icon rose">
              <TrendingUp size={17} />
            </div>
          </div>
          <strong>{formatFlow(totalPositive)}</strong>
          <p>红色曲线代表资金净流入靠前方向</p>
        </article>
        <article className="metric-card">
          <div className="metric-head">
            <span>净流出合计</span>
            <div className="metric-icon amber">
              <TrendingDown size={17} />
            </div>
          </div>
          <strong>{formatFlow(totalNegative)}</strong>
          <p>绿色曲线代表资金净流出靠前方向</p>
        </article>
        <article className="metric-card">
          <div className="metric-head">
            <span>跟踪板块</span>
            <div className="metric-icon indigo">
              <BarChart3 size={17} />
            </div>
          </div>
          <strong>{marketFlowSeries.length}</strong>
          <p>当前展示 15 条板块分时资金曲线</p>
        </article>
      </section>

      <section className="market-layout">
        <section className="panel market-chart-panel">
          <div className="panel-header">
            <div>
              <h2>板块资金分时流向</h2>
              <span>单位：亿元 · mock 数据 · 可替换为真实接口</span>
            </div>
            <div className="market-header-controls">
              <div className="segmented-control" aria-label="市场范围">
                <button type="button" className="active">板块</button>
                <button type="button">行业</button>
                <button type="button">概念</button>
              </div>
              <button type="button" className="replay-button" onClick={replayMarketFlow} disabled={isReplaying}>
                {isReplaying ? <RotateCcw className="spin" size={15} /> : <Play size={15} />}
                <span>{isReplaying ? '回放中' : '回放走势'}</span>
              </button>
            </div>
          </div>
          <div className="market-chart" ref={chartRef} />
        </section>

        <aside className="panel market-rank-panel">
          <div className="panel-header">
            <div>
              <h2>收盘排名</h2>
              <span>末端标签同步图表曲线</span>
            </div>
          </div>

          <div className="flow-rank-group">
            <h3>净流入</h3>
            {leaders.map((item, index) => (
              <article key={item.name} className="flow-rank-card positive">
                <span>{String(index + 1).padStart(2, '0')}</span>
                <strong>{item.name}</strong>
                <em>{formatFlow(item.end)}</em>
              </article>
            ))}
          </div>

          <div className="flow-rank-group">
            <h3>净流出</h3>
            {laggards.map((item, index) => (
              <article key={item.name} className="flow-rank-card negative">
                <span>{String(index + 1).padStart(2, '0')}</span>
                <strong>{item.name}</strong>
                <em>{formatFlow(item.end)}</em>
              </article>
            ))}
          </div>
        </aside>
      </section>
    </div>
  );
}
