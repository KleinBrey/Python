import { useEffect, useRef, useState } from 'react';
import * as echarts from 'echarts/core';
import { LineChart } from 'echarts/charts';
import { GridComponent, LegendComponent, MarkLineComponent, TooltipComponent } from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';

import { timeLabels } from '../data/marketFlowData.js';
import { buildMarketFlowOption } from '../utils/marketFlow.js';

echarts.use([CanvasRenderer, GridComponent, LegendComponent, LineChart, MarkLineComponent, TooltipComponent]);

export function useMarketFlowChart() {
  const chartRef = useRef(null);
  const chartInstanceRef = useRef(null);
  const replayTimerRef = useRef(null);
  const [isReplaying, setIsReplaying] = useState(false);
  const [displayTime, setDisplayTime] = useState(timeLabels.at(-1));

  useEffect(() => {
    if (!chartRef.current) return undefined;
    const chart = echarts.init(chartRef.current);
    chartInstanceRef.current = chart;
    chart.setOption(buildMarketFlowOption());
    const handleResize = () => chart.resize();
    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
      if (replayTimerRef.current) window.clearInterval(replayTimerRef.current);
      chart.dispose();
    };
  }, []);

  function replay() {
    const chart = chartInstanceRef.current;
    if (!chart) return;
    if (replayTimerRef.current) window.clearInterval(replayTimerRef.current);
    let visibleCount = 1;
    setIsReplaying(true);
    setDisplayTime(timeLabels[0]);
    chart.setOption(buildMarketFlowOption(visibleCount), true);
    replayTimerRef.current = window.setInterval(() => {
      visibleCount += 1;
      const currentIndex = Math.min(visibleCount - 1, timeLabels.length - 1);
      setDisplayTime(timeLabels[currentIndex]);
      chart.setOption(buildMarketFlowOption(visibleCount), true);
      if (visibleCount >= timeLabels.length) {
        window.clearInterval(replayTimerRef.current);
        replayTimerRef.current = null;
        setIsReplaying(false);
      }
    }, 95);
  }

  return { chartRef, isReplaying, displayTime, replay };
}
