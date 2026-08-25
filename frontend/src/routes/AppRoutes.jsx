import { Suspense, lazy } from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';

import { Spinner } from '@/shadcn/components/ui/spinner.jsx';

import PlaceholderDashboard from '@/components/PlaceholderDashboard.jsx';
import placeholderStyles from '@/components/PlaceholderDashboard.module.css';
import { defaultDashboardPath } from '@/routes/RouteConfig.js';

const DataSourcesDashboard = lazy(() => import('@/pages/DataSourcesDashboard.jsx'));
const HotRankingsDashboard = lazy(() => import('@/pages/HotRankingsDashboard.jsx'));
const IwencaiSelectorDashboard = lazy(() => import('@/pages/IwencaiSelectorDashboard.jsx'));
const MarketOverview = lazy(() => import('@/pages/MarketOverview.jsx'));
const MongoDashboard = lazy(() => import('@/pages/MongoDashboard.jsx'));
const StrategySignalsDashboard = lazy(() => import('@/pages/StrategySignalsDashboard.jsx'));

function RouteFallback() {
  return (
    <section className={placeholderStyles.placeholder}>
      <Spinner />
      <h2>加载页面</h2>
      <p>正在准备数据和界面</p>
    </section>
  );
}

export default function AppRoutes() {
  return (
    <Suspense fallback={<RouteFallback />}>
      <Routes>
        <Route index element={<Navigate to={defaultDashboardPath} replace />} />
        <Route path="/hot-rankings" element={<HotRankingsDashboard />} />
        <Route path="/market-overview" element={<MarketOverview />} />
        <Route path="/data-sources" element={<DataSourcesDashboard />} />
        <Route path="/database" element={<MongoDashboard />} />
        <Route path="/strategy-signals" element={<StrategySignalsDashboard />} />
        <Route path="/iwencai-selector" element={<IwencaiSelectorDashboard />} />
        <Route path="/chart-center" element={<PlaceholderDashboard dashboardId="chart-center" />} />
        <Route path="*" element={<Navigate to={defaultDashboardPath} replace />} />
      </Routes>
    </Suspense>
  );
}
