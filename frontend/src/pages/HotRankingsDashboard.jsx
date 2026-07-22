import React from 'react';
import { Database, LayoutDashboard, Loader2, RefreshCcw, Search, Table2, TrendingUp } from 'lucide-react';
import MetricCard from '../components/MetricCard.jsx';
import { formatValue, latestRefreshTime, rankingScore, shortTime, trendClass } from '../utils/formatters.js';

function SourceCards({ sourceStats }) {
  return (
    <section className="source-grid" aria-label="数据源统计">
      {sourceStats.map((item) => (
        <article key={item.source} className="source-card">
          <span>{item.source}</span>
          <strong>{item.count} 榜</strong>
          <em>{formatValue(item.rows)} 条记录</em>
        </article>
      ))}
      {!sourceStats.length ? (
        <article className="source-card">
          <span>暂无来源</span>
          <strong>-</strong>
          <em>等待缓存或刷新</em>
        </article>
      ) : null}
    </section>
  );
}

function RankingChart({ ranking }) {
  const rows = (ranking?.rows || []).slice(0, 10);
  const values = rows.map((row) => Math.abs(Number(rankingScore(row))) || 0);
  const max = Math.max(...values, 1);

  return (
    <section className="panel chart-panel">
      <div className="panel-header">
        <div>
          <h2>榜单走势</h2>
          <span>{ranking?.title || '选择一个榜单'}</span>
        </div>
        <div className="segmented-control" aria-label="时间范围">
          <button type="button">今日</button>
          <button type="button" className="active">当前</button>
          <button type="button">缓存</button>
        </div>
      </div>

      <div className="bar-chart" aria-label="前十排名条形图">
        {rows.map((row, index) => {
          const score = Math.abs(Number(rankingScore(row))) || 0;
          const width = Math.max(8, Math.round((score / max) * 100));
          return (
            <div className="bar-row" key={`${ranking.id}-bar-${row.rank}-${row.code || row.name}`}>
              <span>{String(index + 1).padStart(2, '0')}</span>
              <strong>{row.name || row.code || '-'}</strong>
              <div className="bar-track">
                <i style={{ width: `${width}%` }} />
              </div>
              <em>{formatValue(rankingScore(row))}</em>
            </div>
          );
        })}
        {!rows.length ? <div className="empty-state">暂无图表数据</div> : null}
      </div>
    </section>
  );
}

function RankingCards({ rankings, activeRanking, onSelectRanking, onRefreshRanking, refreshingId, refreshingAll }) {
  return (
    <section className="panel rankings-panel">
      <div className="panel-header">
        <div>
          <h2>全部热榜</h2>
          <span>{rankings.length} 个榜单</span>
        </div>
        <Table2 size={18} />
      </div>

      <div className="ranking-list">
        {rankings.map((ranking) => (
          <article
            key={ranking.id}
            className={`ranking-card ${activeRanking?.id === ranking.id ? 'selected' : ''}`}
            onClick={() => onSelectRanking(ranking.id)}
          >
            <div className="ranking-card-head">
              <div>
                <span>{ranking.source}</span>
                <h3>{ranking.title}</h3>
              </div>
              <button
                type="button"
                className="icon-button"
                onClick={(event) => {
                  event.stopPropagation();
                  onRefreshRanking(ranking.id);
                }}
                disabled={refreshingId === ranking.id || refreshingAll}
                title="刷新榜单"
              >
                {refreshingId === ranking.id ? <Loader2 className="spin" size={15} /> : <RefreshCcw size={15} />}
              </button>
            </div>

            {ranking.error ? <div className="inline-error">{ranking.error}</div> : null}

            <ol className="mini-rank">
              {(ranking.rows || []).slice(0, 4).map((row) => (
                <li key={`${ranking.id}-${row.rank}-${row.code || row.name}`}>
                  <span>{row.rank}</span>
                  <strong>{row.name || row.code || '-'}</strong>
                  <em>{formatValue(rankingScore(row))}</em>
                </li>
              ))}
              {!ranking.rows?.length ? <li className="empty-line">暂无缓存</li> : null}
            </ol>

            <footer>
              <span>{formatValue(ranking.rowCount)} 条</span>
              <span>{shortTime(ranking.updatedAt)}</span>
            </footer>
          </article>
        ))}
      </div>
    </section>
  );
}

function RankingTable({ activeRanking, onRefreshRanking, refreshingId, refreshingAll }) {
  return (
    <section className="panel table-panel">
      <div className="panel-header">
        <div>
          <h2>{activeRanking?.title || '热榜详情'}</h2>
          <span>{activeRanking?.source || '-'} · {shortTime(activeRanking?.updatedAt)}</span>
        </div>
        <button
          type="button"
          className="ghost-button"
          onClick={() => onRefreshRanking(activeRanking?.id)}
          disabled={!activeRanking || refreshingId === activeRanking.id || refreshingAll}
        >
          {refreshingId === activeRanking?.id ? <Loader2 className="spin" size={15} /> : <RefreshCcw size={15} />}
          <span>{refreshingId === activeRanking?.id ? '更新中' : '刷新当前'}</span>
        </button>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>排名</th>
              <th>股票</th>
              <th>代码</th>
              <th>热度</th>
              <th>最新价</th>
              <th>涨跌</th>
            </tr>
          </thead>
          <tbody>
            {(activeRanking?.rows || []).map((row) => (
              <tr key={`${activeRanking.id}-${row.rank}-${row.code || row.name}`}>
                <td>{formatValue(row.rank)}</td>
                <td>{row.name || '-'}</td>
                <td>{row.code || '-'}</td>
                <td>{formatValue(row.heat)}</td>
                <td>{formatValue(row.price)}</td>
                <td className={trendClass(row.change)}>{formatValue(row.change)}</td>
              </tr>
            ))}
            {!activeRanking?.rows?.length ? (
              <tr>
                <td colSpan="6" className="empty">暂无数据，点击刷新当前榜单</td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
    </section>
  );
}

export default function HotRankingsDashboard({
  summary,
  rankings,
  activeRanking,
  loading,
  error,
  sourceStats,
  refreshingAll,
  refreshingId,
  onLoadCache,
  onSelectRanking,
  onRefreshRanking,
}) {
  const topRanking = activeRanking?.rows?.[0];

  return (
    <div className="dashboard-content">
      <section className="metric-grid" aria-label="热度概览">
        <MetricCard
          label="数据源"
          value={summary?.dataSource || 'akshare'}
          note="当前后端数据入口"
          icon={Database}
          tone="teal"
        />
        <MetricCard
          label="已配置榜单"
          value={summary?.configuredRankingCount ?? rankings.length}
          note={loading ? '正在读取' : `${rankings.length} 个已返回`}
          icon={LayoutDashboard}
          tone="indigo"
        />
        <MetricCard
          label="缓存榜单"
          value={summary?.hotRankingCount}
          note="MongoDB 中的热榜快照"
          icon={Table2}
          tone="rose"
        />
        <MetricCard
          label="榜首股票"
          value={topRanking?.name || topRanking?.code || '-'}
          note={`最近刷新 ${latestRefreshTime(rankings)}`}
          icon={TrendingUp}
          tone="amber"
        />
      </section>

      {error ? (
        <div className="notice">
          <span>{error}</span>
          <button type="button" className="ghost-button" onClick={onLoadCache}>
            <Search size={15} />
            <span>读取缓存</span>
          </button>
        </div>
      ) : null}

      <SourceCards sourceStats={sourceStats} />

      <section className="dashboard-grid">
        <RankingChart ranking={activeRanking} />
        <RankingCards
          rankings={rankings}
          activeRanking={activeRanking}
          onSelectRanking={onSelectRanking}
          onRefreshRanking={onRefreshRanking}
          refreshingId={refreshingId}
          refreshingAll={refreshingAll}
        />
      </section>

      <RankingTable
        activeRanking={activeRanking}
        onRefreshRanking={onRefreshRanking}
        refreshingId={refreshingId}
        refreshingAll={refreshingAll}
      />
    </div>
  );
}
