import React from 'react';
import { Blocks, ChartCandlestick, Database, Loader2, RefreshCcw } from 'lucide-react';
import { Button } from '@/components/ui/button.jsx';
import MetricCard from '../components/MetricCard.jsx';
import StatusBadge from '../components/StatusBadge.jsx';
import { shortTime, statusLabel } from '../utils/formatters.js';

export default function DataSourcesDashboard({ dataSources, loading, onCheckSources }) {
  const sourceById = Object.fromEntries(dataSources.map((item) => [item.id, item]));
  const hithink = sourceById['hithink-financial'];
  const onlineCount = dataSources.filter((item) => ['online', 'ready'].includes(item.status)).length;

  return (
    <div className="dashboard-content">
      <section className="metric-grid" aria-label="数据源状态">
        <MetricCard
          label="同花顺扶摇"
          value={statusLabel(hithink?.status, '-')}
          note={hithink?.message || '系统唯一结构化证券数据源'}
          icon={Database}
          tone="teal"
        />
        <MetricCard
          label="官方 API Key"
          value={hithink?.credential || '-'}
          note="仅由后端读取，不发送到浏览器"
          icon={ChartCandlestick}
          tone="indigo"
        />
        <MetricCard
          label="已接入数据源"
          value={dataSources.length}
          note={`${onlineCount} 个处于可用或已就绪状态`}
          icon={Blocks}
          tone="rose"
        />
        <MetricCard
          label="检测方式"
          value={loading ? '检测中' : '手动'}
          note="点击检测才会真实请求外部接口"
          icon={RefreshCcw}
          tone="amber"
        />
      </section>

      <section className="panel">
        <div className="panel-header">
          <div>
            <h2>数据源连接状态</h2>
            <span>同花顺扶摇官方 API 的配置与连通情况</span>
          </div>
          <Button type="button" onClick={onCheckSources} disabled={loading}>
            {loading ? <Loader2 className="spin" size={15} /> : <RefreshCcw size={15} />}
            <span>{loading ? '检测中' : '检测连通'}</span>
          </Button>
        </div>

        <div className="source-status-grid">
          {dataSources.map((source) => (
            <article key={source.id} className="status-card">
              <div className="status-card-head">
                <div>
                  <span>{source.type}</span>
                  <h3>{source.name}</h3>
                </div>
                <StatusBadge status={source.status} />
              </div>
              <dl>
                <div>
                  <dt>接入方式</dt>
                  <dd>{source.type}</dd>
                </div>
                <div>
                  <dt>凭证</dt>
                  <dd>{source.credential}</dd>
                </div>
                <div>
                  <dt>最近检测</dt>
                  <dd>{shortTime(source.checkedAt)}</dd>
                </div>
              </dl>
              <p>{source.message}</p>
            </article>
          ))}
          {!dataSources.length ? <div className="empty-state">暂无数据源状态</div> : null}
        </div>
      </section>
    </div>
  );
}
