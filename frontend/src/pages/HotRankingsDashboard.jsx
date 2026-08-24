import { useCallback, useState } from 'react';

import RankingTable from '@/features/hot-rankings/components/RankingTable.jsx';
import StockKlinePanel from '@/features/hot-rankings/components/StockKlinePanel.jsx';
import { useHotStockRanking } from '@/features/hot-rankings/hooks/useHotStockRanking.js';
import { useStockKline } from '@/features/hot-rankings/hooks/useStockKline.js';
import { Loader2, RefreshCcw } from 'lucide-react';
import { Button } from '@/components/ui/button.jsx';
import moment from 'moment';

export default function HotRankingsDashboard() {
  const [selectedStock, setSelectedStock] = useState(null);
  const { ranking, loading: rankingLoading, error: rankingError, refresh } = useHotStockRanking();
  const { data: klineData, loading: klineLoading, error: klineError, loadKline } = useStockKline();

  function formatTimestamp(timestamp) {
    if (!timestamp) return '未刷新';

    const value = moment(timestamp);
    return value.isValid() ? value.format('YYYY-MM-DD HH:mm:ss') : '未刷新';
  }

  const handleStockClick = useCallback(
    stock => {
      setSelectedStock(stock);
      loadKline(stock.thscode);
    },
    [loadKline]
  );

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
        <div className="table-wrap">
          <RankingTable
            ranking={ranking}
            loading={rankingLoading}
            error={rankingError}
            onRefresh={refresh}
            onRowClick={handleStockClick}
          />
          <StockKlinePanel stock={selectedStock} data={klineData} loading={klineLoading} error={klineError} />
        </div>
      </section>
    </div>
  );
}
