import { cn } from '@/shadcn/lib/utils.js';
import { formatFlow } from '../utils/marketFlow.js';
import styles from './MarketOverview.module.css';

function RankingGroup({ title, items, tone }) {
  return <div className={styles.rankGroup}><h3>{title}</h3>{items.map((item, index) => <article key={item.name} className={cn(styles.rankCard, styles[tone])}><span>{String(index + 1).padStart(2, '0')}</span><strong>{item.name}</strong><em>{formatFlow(item.end)}</em></article>)}</div>;
}

export default function FlowRankingPanel({ leaders, laggards }) {
  return (
    <aside className={cn('dashboard-panel', styles.rankPanel)}>
      <div className="dashboard-panel-header"><div><h2>收盘排名</h2><span>末端标签同步图表曲线</span></div></div>
      <RankingGroup title="净流入" items={leaders} tone="positive" />
      <RankingGroup title="净流出" items={laggards} tone="negative" />
    </aside>
  );
}
