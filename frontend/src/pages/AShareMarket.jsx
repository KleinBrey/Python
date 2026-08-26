import { useEffect, useRef, useState } from 'react';

import AShareMarketTable from '@/features/a-share-market/components/AShareMarketTable.jsx';
import styles from '@/features/a-share-market/AShareMarket.module.css';
import { useAShareMarketRanking } from '@/features/a-share-market/hooks/useAShareMarketRanking.js';
import { Loader2, Maximize2, Minimize2, RefreshCcw } from 'lucide-react';
import { Button } from '@/shadcn/components/ui/button.jsx';
import { cn } from '@/shadcn/lib/utils.js';
import moment from 'moment';

export default function AShareMarket() {
  const panelRef = useRef(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const { ranking, loading: rankingLoading, error: rankingError, refresh } = useAShareMarketRanking();

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

    const time = `${value.format('YYYY-MM-DD HH:mm:ss')}｜${value.fromNow()}`;
    return value.isValid() ? time : '未刷新';
  }

  return (
    <div className="dashboard-content">
      <section className={cn('dashboard-panel', 'dashboard-table-panel', styles.panel)} ref={panelRef}>
        <div className="dashboard-panel-header">
          <div>
            <h2>{ranking.title}</h2>
            <span>{rankingError || formatTimestamp(ranking.timestamp)}</span>
          </div>
          <div className={styles.headerActions}>
            <Button
              aria-label={isFullscreen ? '退出全屏' : '全屏显示热榜'}
              aria-pressed={isFullscreen}
              className={cn('dashboard-ghost-button', styles.fullscreenButton)}
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
              className="dashboard-ghost-button"
              variant="outline"
              onClick={refresh}
              disabled={rankingLoading}
            >
              {rankingLoading ? <Loader2 className="dashboard-spin" size={15} /> : <RefreshCcw size={15} />}
              <span>{rankingLoading ? '更新中' : '刷新当前'}</span>
            </Button>
          </div>
        </div>
        <div className={styles.tableWrap}>
          <AShareMarketTable rows={ranking.rows} loading={rankingLoading} />
        </div>
      </section>
    </div>
  );
}
