import RankingTable from '@/features/hot-rankings/components/RankingTable.jsx';
import { useHotStockRanking } from '@/features/hot-rankings/hooks/useHotStockRanking.js';
import { Loader2, RefreshCcw } from 'lucide-react';
import { Button } from '@/components/ui/button.jsx';
import moment from 'moment';

export default function HotRankingsDashboard() {
  const { ranking, loading: rankingLoading, error: rankingError, refresh } = useHotStockRanking();

  function formatTimestamp(timestamp) {
    if (!timestamp) return '未刷新';

    const value = moment(timestamp);
    return value.isValid() ? value.format('YYYY-MM-DD HH:mm:ss') : '未刷新';
  }

  return (
    <div className="dashboard-content">
      <section className="panel table-panel">
        <div className="panel-header">
          <div>
            <h2>{ranking.title}</h2>
            <span>{rankingError || formatTimestamp(ranking.timestamp)}</span>
          </div>
          <Button type="button" className="ghost-button" variant="outline" onClick={refresh} disabled={rankingLoading}>
            {rankingLoading ? <Loader2 className="spin" size={15} /> : <RefreshCcw size={15} />}
            <span>{rankingLoading ? '更新中' : '刷新当前'}</span>
          </Button>
        </div>
        <div className="table-wrap hot-ranking-table-wrap">
          <RankingTable
            ranking={ranking}
            loading={rankingLoading}
          />
        </div>
      </section>
    </div>
  );
}
