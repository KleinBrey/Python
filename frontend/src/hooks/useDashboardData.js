import { useEffect, useMemo, useState } from 'react';
import { apiGet } from '../api/client.js';
import { getDashboardByPath } from '../routes/RouteConfig';

export default function useDashboardData(pathname) {
  const [summary, setSummary] = useState(null);
  const [rankings, setRankings] = useState([]);
  const [dataSources, setDataSources] = useState([]);
  const [databaseStatus, setDatabaseStatus] = useState(null);
  const [activeId, setActiveId] = useState('');
  const [loading, setLoading] = useState(true);
  const [loadingSources, setLoadingSources] = useState(false);
  const [loadingDatabase, setLoadingDatabase] = useState(false);
  const [refreshingAll, setRefreshingAll] = useState(false);
  const [refreshingId, setRefreshingId] = useState('');
  const [error, setError] = useState('');

  const selectedDashboard = useMemo(() => getDashboardByPath(pathname), [pathname]);

  const activeRanking = useMemo(
    () => rankings.find(ranking => ranking.id === activeId) || rankings[0],
    [rankings, activeId]
  );

  const sourceStats = useMemo(() => {
    const grouped = new Map();
    rankings.forEach(ranking => {
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

  async function loadDataSources(check = false) {
    setLoadingSources(true);
    try {
      const payload = await apiGet(`/api/data-sources?check=${check ? 'true' : 'false'}`);
      setDataSources(payload.items || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingSources(false);
    }
  }

  async function loadDatabaseStatus() {
    setLoadingDatabase(true);
    try {
      const payload = await apiGet('/api/database');
      setDatabaseStatus(payload);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingDatabase(false);
    }
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
          setRankings(current => current.map(item => (item.id === ranking.id ? payload.item : item)));
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
      setRankings(current => current.map(ranking => (ranking.id === rankingId ? payload.item : ranking)));
      await loadSummary();
    } catch (err) {
      setError(err.message);
    } finally {
      setRefreshingId('');
    }
  }

  useEffect(() => {
    loadRankings(false);
    loadDataSources(false);
    loadDatabaseStatus();
  }, []);

  useEffect(() => {
    setError('');
    if (pathname === '/data-sources') {
      loadDataSources(false);
    }
    if (pathname === '/database') {
      loadDatabaseStatus();
    }
  }, [pathname]);

  return {
    activeRanking,
    dataSources,
    databaseStatus,
    error,
    loading,
    loadingDatabase,
    loadingSources,
    rankings,
    refreshingAll,
    refreshingId,
    selectedDashboard,
    sourceStats,
    summary,
    loadDataSources,
    loadDatabaseStatus,
    loadRankings,
    refreshAllRankings,
    refreshRanking,
    setActiveId
  };
}
