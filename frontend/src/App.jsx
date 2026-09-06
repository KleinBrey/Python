import { BrowserRouter } from 'react-router-dom';

import { ThemeProvider, TradingCalendarProvider } from '@/contexts';
import Layout from '@/layouts/Layout.jsx';
import AppRoutes from '@/routes/AppRoutes.jsx';

export default function App() {
  return (
    <TradingCalendarProvider>
      <ThemeProvider>
        <BrowserRouter>
          <Layout>
            <AppRoutes />
          </Layout>
        </BrowserRouter>
      </ThemeProvider>
    </TradingCalendarProvider>
  );
}
