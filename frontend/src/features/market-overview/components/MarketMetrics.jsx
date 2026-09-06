import { BarChart3, Clock3, TrendingDown, TrendingUp } from 'lucide-react';

import metricStyles from '@/components/MetricCard.module.css';
import { cn } from '@/shadcn/lib/utils.js';
import { marketFlowSeries } from '../data/marketFlowData.js';
import { formatFlow } from '../utils/marketFlow.js';
import styles from './MarketOverview.module.css';

export default function MarketMetrics({ displayTime, isReplaying, totalPositive, totalNegative }) {
  return (
    <section className="dashboard-metric-grid" aria-label="市场概览">
      <article className={cn(metricStyles.card, styles.hero)}><div className={metricStyles.head}><span>收盘资金流向</span><div className={cn(metricStyles.icon, metricStyles.teal)}><Clock3 size={17} /></div></div><strong>{displayTime}</strong><p>{isReplaying ? '正在回放分时资金曲线' : 'Mock 分时数据，后续可替换为真实板块资金流'}</p></article>
      <article className={metricStyles.card}><div className={metricStyles.head}><span>净流入合计</span><div className={cn(metricStyles.icon, metricStyles.rose)}><TrendingUp size={17} /></div></div><strong>{formatFlow(totalPositive)}</strong><p>红色曲线代表资金净流入靠前方向</p></article>
      <article className={metricStyles.card}><div className={metricStyles.head}><span>净流出合计</span><div className={cn(metricStyles.icon, metricStyles.amber)}><TrendingDown size={17} /></div></div><strong>{formatFlow(totalNegative)}</strong><p>绿色曲线代表资金净流出靠前方向</p></article>
      <article className={metricStyles.card}><div className={metricStyles.head}><span>跟踪板块</span><div className={cn(metricStyles.icon, metricStyles.indigo)}><BarChart3 size={17} /></div></div><strong>{marketFlowSeries.length}</strong><p>当前展示 15 条板块分时资金曲线</p></article>
    </section>
  );
}
