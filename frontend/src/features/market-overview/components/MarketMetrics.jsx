import { BarChart3, Clock3, TrendingDown, TrendingUp } from 'lucide-react';

import { marketFlowSeries } from '../data/marketFlowData.js';
import { formatFlow } from '../utils/marketFlow.js';

export default function MarketMetrics({ displayTime, isReplaying, totalPositive, totalNegative }) {
  return (
    <section className="metric-grid" aria-label="市场概览">
      <article className="metric-card market-hero-card"><div className="metric-head"><span>收盘资金流向</span><div className="metric-icon teal"><Clock3 size={17} /></div></div><strong>{displayTime}</strong><p>{isReplaying ? '正在回放分时资金曲线' : 'Mock 分时数据，后续可替换为真实板块资金流'}</p></article>
      <article className="metric-card"><div className="metric-head"><span>净流入合计</span><div className="metric-icon rose"><TrendingUp size={17} /></div></div><strong>{formatFlow(totalPositive)}</strong><p>红色曲线代表资金净流入靠前方向</p></article>
      <article className="metric-card"><div className="metric-head"><span>净流出合计</span><div className="metric-icon amber"><TrendingDown size={17} /></div></div><strong>{formatFlow(totalNegative)}</strong><p>绿色曲线代表资金净流出靠前方向</p></article>
      <article className="metric-card"><div className="metric-head"><span>跟踪板块</span><div className="metric-icon indigo"><BarChart3 size={17} /></div></div><strong>{marketFlowSeries.length}</strong><p>当前展示 15 条板块分时资金曲线</p></article>
    </section>
  );
}
