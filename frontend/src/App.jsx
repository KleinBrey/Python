import React from 'react';
import { ConfigProvider, theme } from 'antd';
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
    <ConfigProvider
      theme={{
        algorithm: theme.darkAlgorithm,
        token: {
          borderRadius: 8,
          colorPrimary: '#1677ff',
          fontFamily: 'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", sans-serif',
        },
      }}
    >
      <BrowserRouter>
        <DashboardApp />
      </BrowserRouter>
    </ConfigProvider>
  );
}
