import React, { useEffect, useMemo, useRef, useState } from 'react';
import {
  CandlestickSeries,
  ColorType,
  CrosshairMode,
  HistogramSeries,
  LineSeries,
  LineStyle,
  createChart,
} from 'lightweight-charts';
import { Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button.jsx';

const periodOptions = [
  ['daily', '日线'],
  ['weekly', '周线'],
  ['monthly', '月线'],
];

const movingAverages = [
  { days: 5, color: '#f59e0b' },
  { days: 10, color: '#38bdf8' },
  { days: 20, color: '#a78bfa' },
];

function timeKey(value) {
  if (typeof value === 'string' || typeof value === 'number') return String(value);
  if (value && typeof value === 'object' && 'year' in value) {
    const month = String(value.month).padStart(2, '0');
    const day = String(value.day).padStart(2, '0');
    return `${value.year}-${month}-${day}`;
  }
  return '';
}

function chartRows(data) {
  return (data?.rows || [])
    .map((row) => ({
      ...row,
      time: row.date,
      open: Number(row.open),
      high: Number(row.high),
      low: Number(row.low),
      close: Number(row.close),
      volume: Number(row.volume || 0),
    }))
    .filter(
      (row) =>
        row.time &&
        [row.open, row.high, row.low, row.close, row.volume].every(Number.isFinite),
    )
    .sort((left, right) => String(left.time).localeCompare(String(right.time)));
}

function calculateMA(rows, dayCount) {
  let rollingTotal = 0;
  return rows.flatMap((row, index) => {
    rollingTotal += row.close;
    if (index >= dayCount) rollingTotal -= rows[index - dayCount].close;
    if (index < dayCount - 1) return [];
    return [{ time: row.time, value: Number((rollingTotal / dayCount).toFixed(3)) }];
  });
}

function formatPrice(value) {
  return Number.isFinite(Number(value))
    ? Number(value).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 3 })
    : '—';
}

function formatVolume(value) {
  const number = Number(value);
  if (!Number.isFinite(number)) return '—';
  if (number >= 100000000) return `${(number / 100000000).toFixed(2)}亿`;
  if (number >= 10000) return `${(number / 10000).toFixed(1)}万`;
  return number.toLocaleString('zh-CN');
}

function rowSummary(row) {
  if (!row) return null;
  return {
    time: row.time,
    open: row.open,
    high: row.high,
    low: row.low,
    close: row.close,
    volume: row.volume,
    rising: row.close >= row.open,
  };
}

export default function StockKlineChart({ data, stock, loading, error, period, onPeriodChange }) {
  const chartRef = useRef(null);
  const rows = useMemo(() => chartRows(data), [data]);
  const [activeBar, setActiveBar] = useState(() => rowSummary(rows.at(-1)));

  useEffect(() => {
    setActiveBar(rowSummary(rows.at(-1)));
  }, [rows]);

  useEffect(() => {
    const container = chartRef.current;
    if (!container || !rows.length) return undefined;

    const chart = createChart(container, {
      autoSize: true,
      height: 520,
      layout: {
        attributionLogo: true,
        background: { type: ColorType.Solid, color: '#111114' },
        textColor: '#a1a1aa',
        fontFamily: 'Inter, ui-sans-serif, system-ui, sans-serif',
        panes: {
          separatorColor: '#27272a',
          separatorHoverColor: '#3f3f46',
          enableResize: true,
        },
      },
      grid: {
        vertLines: { color: '#202024', style: LineStyle.Dotted },
        horzLines: { color: '#27272a', style: LineStyle.Dotted },
      },
      crosshair: {
        mode: CrosshairMode.Normal,
        vertLine: {
          color: '#71717a',
          labelBackgroundColor: '#27272a',
          style: LineStyle.Dashed,
        },
        horzLine: {
          color: '#71717a',
          labelBackgroundColor: '#27272a',
          style: LineStyle.Dashed,
        },
      },
      rightPriceScale: {
        borderColor: '#3f3f46',
        entireTextOnly: true,
        scaleMargins: { top: 0.12, bottom: 0.08 },
      },
      timeScale: {
        borderColor: '#3f3f46',
        rightOffset: 6,
        barSpacing: 8,
        minBarSpacing: 3,
        fixLeftEdge: false,
        lockVisibleTimeRangeOnResize: true,
        rightBarStaysOnScroll: true,
        timeVisible: false,
      },
      localization: { locale: 'zh-CN' },
      handleScroll: {
        mouseWheel: true,
        pressedMouseMove: true,
        horzTouchDrag: true,
        vertTouchDrag: false,
      },
      handleScale: {
        axisPressedMouseMove: true,
        mouseWheel: true,
        pinch: true,
      },
    });

    const candleSeries = chart.addSeries(CandlestickSeries, {
      upColor: '#ef4444',
      downColor: '#22c55e',
      borderUpColor: '#ef4444',
      borderDownColor: '#22c55e',
      wickUpColor: '#ef4444',
      wickDownColor: '#22c55e',
      priceLineVisible: false,
      lastValueVisible: true,
    });
    candleSeries.setData(
      rows.map(({ time, open, high, low, close }) => ({ time, open, high, low, close })),
    );

    movingAverages.forEach(({ days, color }) => {
      const series = chart.addSeries(LineSeries, {
        color,
        lineWidth: 1,
        priceLineVisible: false,
        lastValueVisible: false,
        crosshairMarkerVisible: false,
        title: `MA${days}`,
      });
      series.setData(calculateMA(rows, days));
    });

    const volumeSeries = chart.addSeries(
      HistogramSeries,
      {
        priceFormat: { type: 'volume' },
        priceLineVisible: false,
        lastValueVisible: false,
      },
      1,
    );
    volumeSeries.setData(
      rows.map((row) => ({
        time: row.time,
        value: row.volume,
        color: row.close >= row.open ? 'rgba(239, 68, 68, 0.72)' : 'rgba(34, 197, 94, 0.72)',
      })),
    );

    const panes = chart.panes();
    if (panes[1]) panes[1].setHeight(120);

    const rowsByTime = new Map(rows.map((row) => [String(row.time), row]));
    const handleCrosshairMove = (parameter) => {
      const selected = parameter.time ? rowsByTime.get(timeKey(parameter.time)) : rows.at(-1);
      setActiveBar(rowSummary(selected || rows.at(-1)));
    };
    chart.subscribeCrosshairMove(handleCrosshairMove);

    if (rows.length > 120) {
      chart.timeScale().setVisibleLogicalRange({ from: rows.length - 120, to: rows.length + 5 });
    } else {
      chart.timeScale().fitContent();
    }

    return () => {
      chart.unsubscribeCrosshairMove(handleCrosshairMove);
      chart.remove();
    };
  }, [rows]);

  return (
    <section className="iwencai-kline">
      <div className="iwencai-kline-header">
        <div>
          <h3>{stock ? `${stock.股票简称 || ''} ${String(stock.股票代码 || '').replace(/\.(SZ|SH|BJ)$/i, '')}` : '个股 K 线'}</h3>
          <span>{data?.dataSource ? `${data.dataSource} · ` : ''}{data?.adjustLabel || '不复权'} · TradingView Lightweight Charts</span>
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
        <div className="kline-state"><Loader2 className="spin" size={24} /><span>正在读取同花顺扶摇历史行情</span></div>
      ) : error ? (
        <div className="kline-state error"><span>{error}</span></div>
      ) : rows.length ? (
        <div className="kline-chart-shell">
          {activeBar ? (
            <div className="kline-legend" aria-live="polite">
              <span className="kline-legend-date">{activeBar.time}</span>
              <span>开 <strong>{formatPrice(activeBar.open)}</strong></span>
              <span>高 <strong>{formatPrice(activeBar.high)}</strong></span>
              <span>低 <strong>{formatPrice(activeBar.low)}</strong></span>
              <span>收 <strong className={activeBar.rising ? 'rise' : 'fall'}>{formatPrice(activeBar.close)}</strong></span>
              <span>量 <strong>{formatVolume(activeBar.volume)}</strong></span>
              {movingAverages.map(({ days, color }) => (
                <span className="kline-ma-key" key={days} style={{ '--ma-color': color }}>MA{days}</span>
              ))}
            </div>
          ) : null}
          <div
            className="kline-canvas"
            ref={chartRef}
            role="img"
            aria-label={`${stock?.股票简称 || '个股'} K线、均线及成交量图`}
          />
        </div>
      ) : (
        <div className="kline-state"><span>点击左侧股票查看 K 线</span></div>
      )}
    </section>
  );
}
