import { cn } from '@/shadcn/lib/utils.js';
import { useMarketFlowChart } from '../hooks/useMarketFlowChart.js';
import { summarizeMarketFlow } from '../utils/marketFlow.js';
import FlowRankingPanel from './FlowRankingPanel.jsx';
import MarketFlowChart from './MarketFlowChart.jsx';
import MarketMetrics from './MarketMetrics.jsx';
import styles from './MarketOverview.module.css';

const summary = summarizeMarketFlow();

export default function MarketOverviewView() {
  const chart = useMarketFlowChart();
  return (
    <div className={cn('dashboard-content', styles.root)}>
      <MarketMetrics displayTime={chart.displayTime} isReplaying={chart.isReplaying} totalPositive={summary.totalPositive} totalNegative={summary.totalNegative} />
      <section className={styles.layout}>
        <MarketFlowChart chartRef={chart.chartRef} isReplaying={chart.isReplaying} onReplay={chart.replay} />
        <FlowRankingPanel leaders={summary.leaders} laggards={summary.laggards} />
      </section>
    </div>
  );
}
