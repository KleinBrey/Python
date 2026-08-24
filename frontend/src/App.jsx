import { BrowserRouter } from 'react-router-dom';

import { ThemeProvider } from '@/contexts';
import Layout from '@/layouts/Layout.jsx';
import AppRoutes from '@/routes/AppRoutes.jsx';

export default function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <Layout>
          <AppRoutes />
        </Layout>
      </BrowserRouter>
    </ThemeProvider>
  );
}
