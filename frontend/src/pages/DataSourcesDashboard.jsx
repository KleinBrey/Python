import React from 'react';
import { Blocks, ChartCandlestick, Database, Loader2, RefreshCcw } from 'lucide-react';
import MetricCard from '../components/MetricCard.jsx';
import StatusBadge from '../components/StatusBadge.jsx';
import { shortTime, statusLabel } from '../utils/formatters.js';

export default function DataSourcesDashboard({ dataSources, loading, onCheckSources }) {
  const sourceById = Object.fromEntries(dataSources.map((item) => [item.id, item]));
  const akshare = sourceById.akshare;
  const tushare = sourceById.tushare;
  const onlineCount = dataSources.filter((item) => ['online', 'ready'].includes(item.status)).length;

  return (
    <div className="dashboard-content">
      <section className="metric-grid" aria-label="数据源状态">
        <MetricCard
          label="AkShare"
          value={statusLabel(akshare?.status, '-')}
          note={akshare?.message || '用于雪球、百度等热榜'}
          icon={Database}
          tone="teal"
        />
        <MetricCard
          label="Tushare"
          value={statusLabel(tushare?.status, '-')}
          note={tushare?.credential || '用于股票池和历史行情'}
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
            <span>AkShare、东方财富、Tushare 的安装、配置和连通情况</span>
          </div>
          <button type="button" onClick={onCheckSources} disabled={loading}>
            {loading ? <Loader2 className="spin" size={15} /> : <RefreshCcw size={15} />}
            <span>{loading ? '检测中' : '检测连通'}</span>
          </button>
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
                  <dt>SDK</dt>
                  <dd>{source.packageAvailable ? '已安装' : '未安装'}</dd>
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
