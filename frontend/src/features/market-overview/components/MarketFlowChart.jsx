import { Play, RotateCcw } from 'lucide-react';

import { Button } from '@/components/ui/button.jsx';

export default function MarketFlowChart({ chartRef, isReplaying, onReplay }) {
  return (
    <section className="panel market-chart-panel">
      <div className="panel-header">
        <div><h2>板块资金分时流向</h2><span>单位：亿元 · mock 数据 · 可替换为真实接口</span></div>
        <div className="market-header-controls">
          <div className="segmented-control" aria-label="市场范围"><Button type="button" size="sm" variant="ghost" className="active">板块</Button><Button type="button" size="sm" variant="ghost">行业</Button><Button type="button" size="sm" variant="ghost">概念</Button></div>
          <Button type="button" className="replay-button" onClick={onReplay} disabled={isReplaying}>{isReplaying ? <RotateCcw className="spin" size={15} /> : <Play size={15} />}<span>{isReplaying ? '回放中' : '回放走势'}</span></Button>
        </div>
      </div>
      <div className="market-chart" ref={chartRef} />
    </section>
  );
}
