import React, { useEffect, useMemo, useRef } from 'react';
import * as echarts from 'echarts/core';
import { BarChart, CandlestickChart, LineChart } from 'echarts/charts';
import {
  AxisPointerComponent,
  DataZoomComponent,
  GridComponent,
  LegendComponent,
  TooltipComponent,
} from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import { Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button.jsx';

echarts.use([
  AxisPointerComponent,
  BarChart,
  CandlestickChart,
  CanvasRenderer,
  DataZoomComponent,
  GridComponent,
  LegendComponent,
  LineChart,
  TooltipComponent,
]);

const periodOptions = [
  ['daily', '日线'],
  ['weekly', '周线'],
  ['monthly', '月线'],
];

function calculateMA(rows, dayCount) {
  return rows.map((_, index) => {
    if (index < dayCount - 1) return '-';
    const sum = rows
      .slice(index - dayCount + 1, index + 1)
      .reduce((total, row) => total + Number(row.close || 0), 0);
    return Number((sum / dayCount).toFixed(2));
  });
}

function buildOption(data) {
  const rows = data?.rows || [];
  const dates = data?.dates || [];
  const candles = data?.candles || [];
  const startPercent = dates.length > 120 ? Math.max(0, 100 - (120 / dates.length) * 100) : 0;
  const volumes = rows.map((row) => ({
    value: row.volume,
    itemStyle: { color: row.close >= row.open ? '#ef4444' : '#22c55e' },
  }));

  return {
    animation: false,
    backgroundColor: 'transparent',
    axisPointer: { link: [{ xAxisIndex: 'all' }] },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
      backgroundColor: '#18181b',
      borderColor: '#3f3f46',
      textStyle: { color: '#f8fafc', fontSize: 12 },
    },
    legend: {
      top: 8,
      left: 10,
      data: ['K线', 'MA5', 'MA10', 'MA20'],
      textStyle: { color: '#a1a1aa' },
    },
    grid: [
      { left: 62, right: 18, top: 48, height: '58%' },
      { left: 62, right: 18, top: '75%', height: '13%' },
    ],
    xAxis: [
      {
        type: 'category',
        data: dates,
        boundaryGap: true,
        axisLine: { lineStyle: { color: '#3f3f46' } },
        axisLabel: { color: '#71717a', hideOverlap: true },
        axisTick: { show: false },
        min: 'dataMin',
        max: 'dataMax',
      },
      {
        type: 'category',
        gridIndex: 1,
        data: dates,
        boundaryGap: true,
        axisLine: { lineStyle: { color: '#3f3f46' } },
        axisLabel: { show: false },
        axisTick: { show: false },
        min: 'dataMin',
        max: 'dataMax',
      },
    ],
    yAxis: [
      {
        scale: true,
        axisLine: { show: false },
        axisLabel: { color: '#a1a1aa' },
        splitLine: { lineStyle: { color: '#27272a', type: 'dashed' } },
      },
      {
        scale: true,
        gridIndex: 1,
        axisLine: { show: false },
        axisLabel: {
          color: '#71717a',
          formatter: (value) => `${Number(value / 10000).toFixed(0)}万`,
        },
        splitLine: { show: false },
      },
    ],
    dataZoom: [
      { type: 'inside', xAxisIndex: [0, 1], start: startPercent, end: 100 },
      {
        type: 'slider',
        xAxisIndex: [0, 1],
        start: startPercent,
        end: 100,
        bottom: 8,
        height: 20,
        borderColor: '#3f3f46',
        fillerColor: 'rgba(59, 130, 246, 0.18)',
        backgroundColor: '#111114',
        dataBackground: { lineStyle: { color: '#52525b' }, areaStyle: { color: '#27272a' } },
        textStyle: { color: '#71717a' },
      },
    ],
    series: [
      {
        name: 'K线',
        type: 'candlestick',
        data: candles,
        itemStyle: {
          color: '#ef4444',
          color0: '#22c55e',
          borderColor: '#ef4444',
          borderColor0: '#22c55e',
        },
      },
      ...[
        [5, '#f59e0b'],
        [10, '#38bdf8'],
        [20, '#a78bfa'],
      ].map(([days, color]) => ({
        name: `MA${days}`,
        type: 'line',
        data: calculateMA(rows, days),
        smooth: true,
        showSymbol: false,
        lineStyle: { width: 1.2, color },
        emphasis: { disabled: true },
      })),
      {
        name: '成交量',
        type: 'bar',
        xAxisIndex: 1,
        yAxisIndex: 1,
        data: volumes,
        barMaxWidth: 7,
      },
    ],
  };
}

export default function StockKlineChart({ data, stock, loading, error, period, onPeriodChange }) {
  const chartRef = useRef(null);
  const option = useMemo(() => buildOption(data), [data]);

  useEffect(() => {
    if (!chartRef.current || !data?.rows?.length) return undefined;
    const chart = echarts.init(chartRef.current, null, { renderer: 'canvas' });
    chart.setOption(option, true);
    const observer = new ResizeObserver(() => chart.resize());
    observer.observe(chartRef.current);
    return () => {
      observer.disconnect();
      chart.dispose();
    };
  }, [data, option]);

  return (
    <section className="iwencai-kline">
      <div className="iwencai-kline-header">
        <div>
          <h3>{stock ? `${stock.股票简称 || ''} ${String(stock.股票代码 || '').replace(/\.(SZ|SH|BJ)$/i, '')}` : '个股 K 线'}</h3>
          <span>{data?.dataSource ? `${data.dataSource} · ` : ''}{data?.adjustLabel || '不复权'} · K线 / 成交量 / MA5 / MA10 / MA20</span>
        </div>
        <div className="kline-periods">
          {periodOptions.map(([value, label]) => (
            <Button
              key={value}
              type="button"
              className={period === value ? 'active' : ''}
              onClick={() => onPeriodChange(value)}
              disabled={!stock || loading}
              size="sm"
              variant="ghost"
            >
              {label}
            </Button>
          ))}
        </div>
      </div>
      {loading ? (
        <div className="kline-state"><Loader2 className="spin" size={24} /><span>正在读取同花顺问财历史行情</span></div>
      ) : error ? (
        <div className="kline-state error"><span>{error}</span></div>
      ) : data?.rows?.length ? (
        <div className="kline-canvas" ref={chartRef} />
      ) : (
        <div className="kline-state"><span>点击左侧股票查看 K 线</span></div>
      )}
    </section>
  );
}
