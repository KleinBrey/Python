import { useEffect, useRef, useState } from 'react';
import { BookOpenText, ChevronRight, Loader2, Maximize2, Minimize2, RefreshCcw } from 'lucide-react';
import moment from 'moment';
import { Button } from '@/shadcn/components/ui/button.jsx';
import { cn } from '@/shadcn/lib/utils.js';
import StrategyResultsTable from './StrategyResultsTable.jsx';
import styles from './StrategySignals.module.css';

function formatTimestamp(value) {
  if (!value) return '尚未运行';
  const timestamp = moment(value);
  return timestamp.isValid() ? timestamp.format('YYYY-MM-DD HH:mm:ss') : '尚未运行';
}

export default function StrategySignalsView({ state }) {
  const panelRef = useRef(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const { strategies, activeStrategyId, result, columnDefs, loading, error, selectStrategy, refresh } = state;
  const activeStrategy = result?.strategy || strategies.find(strategy => strategy.id === activeStrategyId);
  const rows = result?.items || [];

  useEffect(() => {
    function handleFullscreenChange() {
      setIsFullscreen(document.fullscreenElement === panelRef.current);
    }

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
      console.error('切换策略结果全屏失败', fullscreenError);
    }
  }

  return (
    <div className={cn('dashboard-content', styles.root)}>
      <aside className={cn('dashboard-panel', styles.strategySidebar)} aria-label="策略列表">
        <div className={styles.sidebarHeader}>
          <span>策略列表</span>
          <small>{strategies.length}</small>
        </div>
        <nav className={styles.strategyList}>
          {strategies.map(strategy => {
            const active = strategy.id === activeStrategyId;
            return (
              <button
                key={strategy.id}
                type="button"
                className={cn(styles.strategyItem, active && styles.strategyItemActive)}
                onClick={() => selectStrategy(strategy.id)}
                aria-current={active ? 'page' : undefined}
              >
                <span className={styles.strategyIcon}>
                  <BookOpenText size={17} />
                </span>
                <span className={styles.strategyText}>
                  <strong>{strategy.name}</strong>
                  <small>Python 策略</small>
                </span>
                <ChevronRight size={16} />
              </button>
            );
          })}
          {!strategies.length && !loading ? <p className={styles.noStrategy}>暂无可用策略</p> : null}
        </nav>
      </aside>

      <section className={cn('dashboard-panel', 'dashboard-table-panel', styles.resultPanel)} ref={panelRef}>
        <div className="dashboard-panel-header">
          <div>
            <h2>{activeStrategy?.name || '策略结果'}</h2>
            <span>{error || `最近运行：${formatTimestamp(result?.generated_at)}`}</span>
          </div>
          <div className={styles.headerActions}>
            <Button
              type="button"
              className={cn('dashboard-ghost-button', styles.fullscreenButton)}
              variant="outline"
              size="icon-lg"
              onClick={toggleFullscreen}
              aria-label={isFullscreen ? '退出全屏' : '全屏显示策略结果'}
              aria-pressed={isFullscreen}
              title={isFullscreen ? '退出全屏' : '全屏显示策略结果'}
            >
              {isFullscreen ? <Minimize2 size={18} /> : <Maximize2 size={18} />}
            </Button>
            <Button
              type="button"
              className="dashboard-ghost-button"
              onClick={refresh}
              disabled={loading || !activeStrategyId}
              variant="outline"
            >
              {loading ? <Loader2 className="dashboard-spin" size={15} /> : <RefreshCcw size={15} />}
              <span>{loading ? '运行中' : '重新运行'}</span>
            </Button>
          </div>
        </div>

        {activeStrategy ? (
          <div className={styles.strategySummary}>
            <div>
              <span>命中股票</span>
              <strong>{loading && !result ? '-' : (result?.count ?? 0)}</strong>
            </div>
            <div>
              <span>交易日期</span>
              <strong>{result?.trade_date || '-'}</strong>
            </div>
            <div>
              <span>策略条件</span>
              <strong>{activeStrategy.rules?.[0] || '-'}</strong>
            </div>
            <div>
              <span>策略条件</span>
              <strong>{activeStrategy.rules?.[1] || '-'}</strong>
            </div>
            <p title={activeStrategy.description}>{activeStrategy.description}</p>
          </div>
        ) : null}

        {error ? <div className={styles.errorNotice}>{error}</div> : null}
        <div className={styles.tableWrap}>
          <StrategyResultsTable rows={rows} columnDefs={columnDefs} loading={loading} />
        </div>
      </section>
    </div>
  );
}
