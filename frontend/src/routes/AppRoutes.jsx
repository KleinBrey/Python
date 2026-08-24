import React, { Suspense, lazy } from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';
import { Spinner } from '@/components/ui/spinner.jsx';
import PlaceholderDashboard from '../components/PlaceholderDashboard.jsx';
import { defaultDashboardPath } from './RouteConfig.js';
import DataSourcesDashboard from '../pages/DataSourcesDashboard.jsx';
import HotRankingsDashboard from '../pages/HotRankingsDashboard.jsx';
import MongoDashboard from '../pages/MongoDashboard.jsx';

const MarketOverview = lazy(() => import('../pages/MarketOverview.jsx'));
const StrategySignalsDashboard = lazy(() => import('../pages/StrategySignalsDashboard.jsx'));
const IwencaiSelectorDashboard = lazy(() => import('../pages/IwencaiSelectorDashboard.jsx'));

export default function AppRoutes({ dashboard }) {
  return (
    <Routes>
      <Route index element={<Navigate to={defaultDashboardPath} replace />} />
      <Route
        path="/hot-rankings"
        element={<HotRankingsDashboard />}
      />
      <Route
        path="/market-overview"
        element={
          <Suspense
            fallback={
              <section className="placeholder">
                <Spinner />
                <h2>加载市场概览</h2>
                <p>正在准备 ECharts 图表</p>
              </section>
            }
          >
            <MarketOverview />
          </Suspense>
        }
      />
      <Route
        path="/data-sources"
        element={
          <DataSourcesDashboard
            dataSources={dashboard.dataSources}
            loading={dashboard.loadingSources}
            onCheckSources={() => dashboard.loadDataSources(true)}
          />
        }
      />
      <Route
        path="/database"
        element={
          <MongoDashboard
            databaseStatus={dashboard.databaseStatus}
            loading={dashboard.loadingDatabase}
            onRefreshDatabase={dashboard.loadDatabaseStatus}
          />
        }
      />
      <Route
        path="/strategy-signals"
        element={
          <Suspense
            fallback={
              <section className="placeholder">
                <Spinner />
                <h2>加载策略来源</h2>
                <p>正在读取策略股票列表</p>
              </section>
            }
          >
            <StrategySignalsDashboard />
          </Suspense>
        }
      />
      <Route
        path="/iwencai-selector"
        element={
          <Suspense
            fallback={
              <section className="placeholder">
                <Spinner />
                <h2>加载问财选股</h2>
                <p>正在准备自然语言查询页面</p>
              </section>
            }
          >
            <IwencaiSelectorDashboard />
          </Suspense>
        }
      />
      <Route path="/chart-center" element={<PlaceholderDashboard dashboardId="chart-center" />} />
      <Route path="*" element={<Navigate to={defaultDashboardPath} replace />} />
    </Routes>
  );
}
