import React from 'react';
import { BrowserRouter, useLocation } from 'react-router-dom';
import Layout from './layouts/Layout.jsx';
import AppRoutes from './routes/AppRoutes.jsx';
import useDashboardData from './hooks/useDashboardData.js';
import { ThemeProvider } from './contexts';

function DashboardApp () {
  const location = useLocation();
  console.log('DashboardApp location:', location);
  const dashboard = useDashboardData(location.pathname);

  return (
    <ThemeProvider>
      <Layout
        selectedDashboard={dashboard.selectedDashboard}
        refreshingAll={dashboard.refreshingAll}
        onRefreshAll={dashboard.refreshAllRankings}
      >
        <AppRoutes dashboard={dashboard} />
      </Layout>
    </ThemeProvider>

  );
}


export default function App () {
  return (
    <BrowserRouter>
      <DashboardApp />
    </BrowserRouter>
  );
}
