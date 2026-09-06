import { BarChart3, Blocks, Database, Loader2, RefreshCcw, Table2 } from 'lucide-react';

import MetricCard from '@/components/MetricCard.jsx';
import StatusBadge from '@/components/StatusBadge.jsx';
import { Button } from '@/shadcn/components/ui/button.jsx';
import { cn } from '@/shadcn/lib/utils.js';
import { formatValue, shortTime } from '@/utils/formatters.js';
import { buildDatabaseViewModel } from '../utils/databaseViewModel.js';
import styles from './DatabaseView.module.css';

export default function DatabaseView({ databaseStatus, loading, error, onRefresh }) {
  const { collections, totalRows, previewCollection, previewRows, previewColumns } =
    buildDatabaseViewModel(databaseStatus);

  return (
    <div className="dashboard-content">
      <section className="dashboard-metric-grid" aria-label="MongoDB 状态">
        <MetricCard label="MongoDB" value={databaseStatus?.ok ? '已连接' : '未连接'} note={databaseStatus?.uri || 'mongodb://localhost:27017/'} icon={Database} tone="teal" />
        <MetricCard label="数据库" value={databaseStatus?.name || '-'} note={`最近检测 ${shortTime(databaseStatus?.checkedAt)}`} icon={Table2} tone="indigo" />
        <MetricCard label="集合数" value={collections.length} note="项目当前登记的集合" icon={Blocks} tone="rose" />
        <MetricCard label="总记录" value={totalRows} note="按集合 count 汇总" icon={BarChart3} tone="amber" />
      </section>

      {error ? <div className="dashboard-notice">{error}</div> : null}

      <section className="dashboard-panel">
        <div className="dashboard-panel-header">
          <div><h2>数据库内容</h2><span>先看连接状态，再看每个集合的记录数量和少量预览</span></div>
          <Button type="button" onClick={() => onRefresh()} disabled={loading}>
            {loading ? <Loader2 className="dashboard-spin" size={15} /> : <RefreshCcw size={15} />}
            <span>{loading ? '刷新中' : '刷新状态'}</span>
          </Button>
        </div>
        <div className={styles.collectionGrid}>
          {collections.map(collection => (
            <article key={collection.id} className={styles.collectionCard}>
              <span>{collection.title}</span><strong>{formatValue(collection.count)}</strong><em>{collection.id}</em>
            </article>
          ))}
          {!collections.length ? <div className="dashboard-empty-state">暂无集合状态</div> : null}
        </div>
      </section>

      <section className={cn('dashboard-panel', 'dashboard-table-panel')}>
        <div className="dashboard-panel-header">
          <div><h2>{previewCollection?.title || '集合预览'}</h2><span>{previewCollection?.id || '暂无可预览集合'}</span></div>
          <StatusBadge status={databaseStatus?.ok ? 'online' : 'offline'} label={databaseStatus?.ok ? 'MongoDB 已连接' : 'MongoDB 未连接'} />
        </div>
        <div className="dashboard-table-wrap">
          <table className={styles.previewTable}>
            <thead><tr>{previewColumns.map(column => <th key={column}>{column}</th>)}{!previewColumns.length ? <th>状态</th> : null}</tr></thead>
            <tbody>
              {previewRows.map((row, index) => (
                <tr key={`${previewCollection.id}-${index}`}>{previewColumns.map(column => <td key={column}>{formatValue(row[column])}</td>)}</tr>
              ))}
              {!previewRows.length ? (
                <tr><td colSpan={Math.max(previewColumns.length, 1)} className="dashboard-empty">{databaseStatus?.ok ? '当前集合暂无数据' : 'MongoDB 未连接，无法读取内容'}</td></tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
