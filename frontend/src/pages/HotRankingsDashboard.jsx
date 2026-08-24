import { useCallback, useState } from 'react';

import RankingTable from '@/features/hot-rankings/components/RankingTable.jsx';
import StockKlinePanel from '@/features/hot-rankings/components/StockKlinePanel.jsx';
import { useHotStockRanking } from '@/features/hot-rankings/hooks/useHotStockRanking.js';
import { useStockKline } from '@/features/hot-rankings/hooks/useStockKline.js';

export default function HotRankingsDashboard() {
  const [selectedStock, setSelectedStock] = useState(null);
  const { ranking, loading: rankingLoading, error: rankingError, refresh } = useHotStockRanking();
  const {
    data: klineData,
    loading: klineLoading,
    error: klineError,
    loadKline
  } = useStockKline();

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
        <div className="table-wrap">
          <RankingTable
            ranking={ranking}
            loading={rankingLoading}
            error={rankingError}
            onRefresh={refresh}
            onRowClick={handleStockClick}
          />
          <StockKlinePanel
            stock={selectedStock}
            data={klineData}
            loading={klineLoading}
            error={klineError}
          />
        </div>
      </section>
    </div>
  );
}
