import React from 'react';
import { BrowserRouter, useLocation } from 'react-router-dom';
import AppLayout from './layouts/AppLayout.jsx';
import AppRoutes from './routes/AppRoutes.jsx';
import useDashboardData from './hooks/useDashboardData.js';

function DashboardApp() {
  const location = useLocation();
  const dashboard = useDashboardData(location.pathname);

  return (
    <AppLayout
      selectedDashboard={dashboard.selectedDashboard}
      refreshingAll={dashboard.refreshingAll}
      onRefreshAll={dashboard.refreshAllRankings}
    >
      <AppRoutes dashboard={dashboard} />
    </AppLayout>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <DashboardApp />
    </BrowserRouter>
  );
}
