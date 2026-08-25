import { FileJson2, ListFilter, Search, Sparkles } from 'lucide-react';

import MetricCard from '@/components/MetricCard.jsx';
import { cn } from '@/shadcn/lib/utils.js';
import QueryPanel from './QueryPanel.jsx';
import ResultsPanel from './ResultsPanel.jsx';
import styles from './IwencaiSelector.module.css';

export default function IwencaiSelectorView({ queryState, marketData }) {
  const { query, setQuery, result, status, loading, error, rows, reportedCount, queryStatus, apiKeyBadge, submitQuery } = queryState;
  return (
    <div className={cn('dashboard-content', styles.root)}>
      <section className="dashboard-metric-grid" aria-label="问财查询概览">
        <MetricCard label="符合条件" value={reportedCount} note="同花顺问财返回的股票总数" icon={ListFilter} tone="teal" />
        <MetricCard label="已获取" value={rows.length} note="当前已完整获取的结果行数" icon={FileJson2} tone="indigo" />
        <MetricCard label="分页数量" value={result?.pages_fetched ?? '-'} note="自动分页获取，无需手工翻页" icon={Search} tone="rose" />
        <MetricCard label="查询状态" value={queryStatus} note="API Key 仅保存在本机后端" icon={Sparkles} tone="amber" />
      </section>
      <QueryPanel query={query} onQueryChange={setQuery} status={status} apiKeyBadge={apiKeyBadge} loading={loading} onSubmit={submitQuery} />
      {!status?.configured && status ? <div className="dashboard-notice">未配置 IWENCAI_API_KEY，请先在环境变量或 ~/.zshrc 中配置后重启后端。</div> : null}
      {error ? <div className="dashboard-notice">{error}</div> : null}
      <ResultsPanel result={result} rows={rows} marketData={marketData} />
    </div>
  );
}
