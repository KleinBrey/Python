import { Braces, FileSearch, Layers3, ListChecks, Loader2, RefreshCcw } from 'lucide-react';

import MetricCard from '@/components/MetricCard.jsx';
import { Button } from '@/shadcn/components/ui/button.jsx';
import SourceCard from './SourceCard.jsx';
import StockTable from './StockTable.jsx';

const filters = [['all', '全部来源'], ['iwencai', '同花顺问财'], ['handwritten', '手写策略']];

export default function StrategySignalsView({ state }) {
  const { sources, stocks, activeSource, sourceCountById, loading, error, selectSource, refresh } = state;
  return (
    <div className="dashboard-content strategy-dashboard">
      <section className="metric-grid" aria-label="策略来源概览">
        <MetricCard label="策略来源" value={sources.length || 2} note="问财选股 + Python 手写策略" icon={Layers3} tone="indigo" />
        <MetricCard label="股票记录" value={stocks.length} note="当前筛选来源返回的记录" icon={ListChecks} tone="teal" />
        <MetricCard label="问财选股" value={sourceCountById.iwencai ?? '-'} note="读取最新问财导出结果" icon={FileSearch} tone="rose" />
        <MetricCard label="手写策略" value={sourceCountById.handwritten ?? '-'} note="项目内 Python 策略结果" icon={Braces} tone="amber" />
      </section>
      <section className="strategy-toolbar">
        <div className="strategy-source-filter" aria-label="策略来源筛选">
          {filters.map(([id, label]) => <Button key={id} type="button" className={activeSource === id ? 'active' : ''} onClick={() => selectSource(id)} disabled={loading} size="sm" variant="ghost">{label}</Button>)}
        </div>
        <Button type="button" className="ghost-button" onClick={refresh} disabled={loading} variant="outline">{loading ? <Loader2 className="spin" size={15} /> : <RefreshCcw size={15} />}重新读取</Button>
      </section>
      {error ? <div className="notice">{error}</div> : null}
      <section className="strategy-source-grid">{sources.map(source => <SourceCard key={source.id} source={source} />)}</section>
      <StockTable stocks={stocks} />
    </div>
  );
}
