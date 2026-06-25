import React, { useEffect, useMemo, useState } from 'react';

const API_BASE_URLS = [
  import.meta.env.VITE_API_BASE_URL,
  'http://127.0.0.1:8001',
].filter(Boolean);

async function apiGet(path) {
  let lastError = null;

  for (const baseUrl of API_BASE_URLS) {
    try {
      const response = await fetch(`${baseUrl}${path}`);
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.error || '请求失败');
      }
      return payload;
    } catch (err) {
      lastError = err;
    }
  }

  throw lastError || new Error('请求失败');
}

function formatValue(value) {
  if (value === null || value === undefined || value === '') return '-';
  const number = Number(value);
  if (Number.isFinite(number)) {
    return number.toLocaleString('zh-CN', { maximumFractionDigits: 2 });
  }
  return String(value);
}

function shortTime(value) {
  if (!value) return '未刷新';
  return value.replace('T', ' ');
}

function rankingScore(row) {
  return row.heat ?? row.change ?? row.price ?? '-';
}

function App() {
  const [summary, setSummary] = useState(null);
  const [rankings, setRankings] = useState([]);
  const [activeId, setActiveId] = useState('');
  const [loading, setLoading] = useState(true);
  const [refreshingAll, setRefreshingAll] = useState(false);
  const [refreshingId, setRefreshingId] = useState('');
  const [error, setError] = useState('');

  const activeRanking = useMemo(
    () => rankings.find((ranking) => ranking.id === activeId) || rankings[0],
    [rankings, activeId],
  );

  const sourceStats = useMemo(() => {
    const grouped = new Map();
    rankings.forEach((ranking) => {
      const current = grouped.get(ranking.source) || { source: ranking.source, count: 0, rows: 0 };
      current.count += 1;
      current.rows += ranking.rowCount || 0;
      grouped.set(ranking.source, current);
    });
    return [...grouped.values()];
  }, [rankings]);

  async function loadSummary() {
    const payload = await apiGet('/api/summary');
    setSummary(payload);
  }

  async function loadRankings(refresh = false) {
    setLoading(!refresh);
    setRefreshingAll(refresh);
    setError('');
    try {
      const payload = await apiGet(`/api/hot-rankings?limit=80&refresh=${refresh ? 'true' : 'false'}`);
      const items = payload.items || [];
      setRankings(items);
      if (!activeId && items.length) {
        setActiveId(items[0].id);
      }
      if (payload.mongoAvailable === false) {
        setError('MongoDB 未连接，热榜缓存暂时不可用。');
      }
      await loadSummary();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
      setRefreshingAll(false);
    }
  }

  async function refreshAllRankings() {
    setRefreshingAll(true);
    setError('');
    try {
      let items = rankings;
      if (!items.length) {
        const payload = await apiGet('/api/hot-rankings?limit=80&refresh=false');
        items = payload.items || [];
        setRankings(items);
        if (!activeId && items.length) {
          setActiveId(items[0].id);
        }
      }

      for (const ranking of items) {
        try {
          const payload = await apiGet(`/api/hot-rankings/${ranking.id}?limit=120&refresh=true`);
          setRankings((current) => current.map((item) => (
            item.id === ranking.id ? payload.item : item
          )));
        } catch (err) {
          setError(err.message);
        }
      }
      await loadSummary();
    } finally {
      setRefreshingAll(false);
      setRefreshingId('');
    }
  }

  async function refreshRanking(rankingId) {
    if (!rankingId) return;
    setRefreshingId(rankingId);
    setError('');
    try {
      const payload = await apiGet(`/api/hot-rankings/${rankingId}?limit=120&refresh=true`);
      setRankings((current) => current.map((ranking) => (
        ranking.id === rankingId ? payload.item : ranking
      )));
      await loadSummary();
    } catch (err) {
      setError(err.message);
    } finally {
      setRefreshingId('');
    }
  }

  useEffect(() => {
    loadRankings(false);
  }, []);

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">AkShare / MongoDB</p>
          <h1>股票热度排行榜</h1>
        </div>
        <div className="actions">
          <button type="button" onClick={() => loadRankings(false)} disabled={loading || refreshingAll}>
            读取缓存
          </button>
          <button type="button" className="secondary" onClick={refreshAllRankings} disabled={refreshingAll}>
            {refreshingAll ? '刷新中' : '刷新全部'}
          </button>
        </div>
      </header>

      <section className="metrics" aria-label="热度概览">
        <article>
          <span>数据源</span>
          <strong>{summary?.dataSource || 'akshare'}</strong>
        </article>
        <article>
          <span>已配置榜单</span>
          <strong>{formatValue(summary?.configuredRankingCount ?? rankings.length)}</strong>
        </article>
        <article>
          <span>缓存榜单</span>
          <strong>{formatValue(summary?.hotRankingCount)}</strong>
        </article>
        <article>
          <span>平台数</span>
          <strong>{formatValue(sourceStats.length)}</strong>
        </article>
      </section>

      {error ? <div className="notice">{error}</div> : null}

      <section className="source-strip">
        {sourceStats.map((item) => (
          <article key={item.source}>
            <span>{item.source}</span>
            <strong>{item.count} 榜</strong>
            <em>{formatValue(item.rows)} 条</em>
          </article>
        ))}
      </section>

      <section className="workspace">
        <div className="ranking-grid">
          <div className="section-heading">
            <h2>全部热榜</h2>
            <span>{loading ? '加载中' : `${rankings.length} 个`}</span>
          </div>

          <div className="ranking-cards">
            {rankings.map((ranking) => (
              <article
                key={ranking.id}
                className={`ranking-card ${activeRanking?.id === ranking.id ? 'selected' : ''}`}
                onClick={() => setActiveId(ranking.id)}
              >
                <div className="card-head">
                  <div>
                    <span>{ranking.source}</span>
                    <h3>{ranking.title}</h3>
                  </div>
                  <button
                    type="button"
                    onClick={(event) => {
                      event.stopPropagation();
                      refreshRanking(ranking.id);
                    }}
                    disabled={refreshingId === ranking.id || refreshingAll}
                  >
                    {refreshingId === ranking.id ? '更新中' : '刷新'}
                  </button>
                </div>
                <p>{ranking.description}</p>
                {ranking.error ? <div className="inline-error">{ranking.error}</div> : null}
                <ol className="mini-rank">
                  {(ranking.rows || []).slice(0, 6).map((row) => (
                    <li key={`${ranking.id}-${row.rank}-${row.code || row.name}`}>
                      <span>{row.rank}</span>
                      <strong>{row.name || row.code || '-'}</strong>
                      <em>{formatValue(rankingScore(row))}</em>
                    </li>
                  ))}
                  {!ranking.rows?.length ? <li className="empty-line">暂无缓存，点击刷新</li> : null}
                </ol>
                <footer>
                  <span>{formatValue(ranking.rowCount)} 条</span>
                  <span>{shortTime(ranking.updatedAt)}</span>
                </footer>
              </article>
            ))}
          </div>
        </div>

        <aside className="detail-panel">
          <div className="section-heading">
            <div>
              <h2>{activeRanking?.title || '热榜详情'}</h2>
              <span>{activeRanking?.function || '-'}</span>
            </div>
            <button
              type="button"
              className="secondary"
              onClick={() => refreshRanking(activeRanking?.id)}
              disabled={!activeRanking || refreshingId === activeRanking.id || refreshingAll}
            >
              {refreshingId === activeRanking?.id ? '更新中' : '刷新当前'}
            </button>
          </div>

          <div className="detail-meta">
            <article>
              <span>平台</span>
              <strong>{activeRanking?.source || '-'}</strong>
            </article>
            <article>
              <span>更新时间</span>
              <strong>{shortTime(activeRanking?.updatedAt)}</strong>
            </article>
          </div>

          <div className="table-wrap detail-table">
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
                    <td className={Number(row.change) >= 0 ? 'up' : 'down'}>{formatValue(row.change)}</td>
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
        </aside>
      </section>
    </main>
  );
}

export default App;
