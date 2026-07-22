import React, { Suspense, lazy } from 'react';
import { Spin } from 'antd';
import { Navigate, Route, Routes } from 'react-router-dom';
import PlaceholderDashboard from '../components/PlaceholderDashboard.jsx';
import { defaultDashboardPath } from '../config/dashboardRegistry.js';
import DataSourcesDashboard from '../pages/DataSourcesDashboard.jsx';
import HotRankingsDashboard from '../pages/HotRankingsDashboard.jsx';
import MongoDashboard from '../pages/MongoDashboard.jsx';

const MarketOverview = lazy(() => import('../pages/MarketOverview.jsx'));

export default function AppRoutes({ dashboard }) {
  return (
    <Routes>
      <Route index element={<Navigate to={defaultDashboardPath} replace />} />
      <Route
        path="/hot-rankings"
        element={(
          <HotRankingsDashboard
            summary={dashboard.summary}
            rankings={dashboard.rankings}
            activeRanking={dashboard.activeRanking}
            loading={dashboard.loading}
            error={dashboard.error}
            sourceStats={dashboard.sourceStats}
            refreshingAll={dashboard.refreshingAll}
            refreshingId={dashboard.refreshingId}
            onLoadCache={() => dashboard.loadRankings(false)}
            onSelectRanking={dashboard.setActiveId}
            onRefreshRanking={dashboard.refreshRanking}
          />
        )}
      />
      <Route
        path="/market-overview"
        element={(
          <Suspense fallback={<section className="placeholder"><Spin /><h2>加载市场概览</h2><p>正在准备 ECharts 图表</p></section>}>
            <MarketOverview />
          </Suspense>
        )}
      />
      <Route
        path="/data-sources"
        element={(
          <DataSourcesDashboard
            dataSources={dashboard.dataSources}
            loading={dashboard.loadingSources}
            onCheckSources={() => dashboard.loadDataSources(true)}
          />
        )}
      />
      <Route
        path="/database"
        element={(
          <MongoDashboard
            databaseStatus={dashboard.databaseStatus}
            loading={dashboard.loadingDatabase}
            onRefreshDatabase={dashboard.loadDatabaseStatus}
          />
        )}
      />
      <Route path="/strategy-signals" element={<PlaceholderDashboard dashboardId="strategy-signals" />} />
      <Route path="/chart-center" element={<PlaceholderDashboard dashboardId="chart-center" />} />
      <Route path="*" element={<Navigate to={defaultDashboardPath} replace />} />
    </Routes>
  );
}
