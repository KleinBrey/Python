import { useEffect, useRef, useState } from 'react';

import RankingTable from '@/features/hot-rankings/components/RankingTable.jsx';
import { useHotStockRanking } from '@/features/hot-rankings/hooks/useHotStockRanking.js';
import { Loader2, Maximize2, Minimize2, RefreshCcw } from 'lucide-react';
import { Button } from '@/shadcn/components/ui/button.jsx';
import moment from 'moment';

export default function HotRankingsDashboard() {
  const panelRef = useRef(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const { ranking, loading: rankingLoading, error: rankingError, refresh } = useHotStockRanking();

  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(document.fullscreenElement === panelRef.current);
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => document.removeEventListener('fullscreenchange', handleFullscreenChange);
  }, []);

  async function toggleFullscreen() {
    try {
      if (document.fullscreenElement) {
        await document.exitFullscreen();
      } else {
        await panelRef.current?.requestFullscreen();
      }
    } catch (fullscreenError) {
      console.error('切换热榜全屏失败', fullscreenError);
    }
  }

  function formatTimestamp(timestamp) {
    if (!timestamp) return '未刷新';

    const value = moment(timestamp);
    return value.isValid() ? value.format('YYYY-MM-DD HH:mm:ss') : '未刷新';
  }

  return (
    <div className="dashboard-content">
      <section className="panel table-panel hot-ranking-panel" ref={panelRef}>
        <div className="panel-header">
          <div>
            <h2>{ranking.title}</h2>
            <span>{rankingError || formatTimestamp(ranking.timestamp)}</span>
          </div>
          <div className="hot-ranking-header-actions">
            <Button
              aria-label={isFullscreen ? '退出全屏' : '全屏显示热榜'}
              aria-pressed={isFullscreen}
              className="ghost-button hot-ranking-fullscreen-button"
              onClick={toggleFullscreen}
              size="icon-lg"
              title={isFullscreen ? '退出全屏' : '全屏显示热榜'}
              type="button"
              variant="outline"
            >
              {isFullscreen ? <Minimize2 size={18} /> : <Maximize2 size={18} />}
            </Button>
            <Button
              type="button"
              className="ghost-button"
              variant="outline"
              onClick={refresh}
              disabled={rankingLoading}
            >
              {rankingLoading ? <Loader2 className="spin" size={15} /> : <RefreshCcw size={15} />}
              <span>{rankingLoading ? '更新中' : '刷新当前'}</span>
            </Button>
          </div>
        </div>
        <div className="table-wrap hot-ranking-table-wrap">
          <RankingTable ranking={ranking} loading={rankingLoading} />
        </div>
      </section>
    </div>
  );
}
