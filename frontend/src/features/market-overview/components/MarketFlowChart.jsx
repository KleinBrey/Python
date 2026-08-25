import { Play, RotateCcw } from 'lucide-react';

import { Button } from '@/shadcn/components/ui/button.jsx';
import { cn } from '@/shadcn/lib/utils.js';
import styles from './MarketOverview.module.css';

export default function MarketFlowChart({ chartRef, isReplaying, onReplay }) {
  return (
    <section className={cn('dashboard-panel', styles.chartPanel)}>
      <div className="dashboard-panel-header">
        <div><h2>板块资金分时流向</h2><span>单位：亿元 · mock 数据 · 可替换为真实接口</span></div>
        <div className={styles.headerControls}>
          <div className={styles.segmentedControl} aria-label="市场范围"><Button type="button" size="sm" variant="ghost">板块</Button><Button type="button" size="sm" variant="ghost">行业</Button><Button type="button" size="sm" variant="ghost">概念</Button></div>
          <Button type="button" className={styles.replayButton} onClick={onReplay} disabled={isReplaying}>{isReplaying ? <RotateCcw className="dashboard-spin" size={15} /> : <Play size={15} />}<span>{isReplaying ? '回放中' : '回放走势'}</span></Button>
        </div>
      </div>
      <div className={styles.chart} ref={chartRef} />
    </section>
  );
}
