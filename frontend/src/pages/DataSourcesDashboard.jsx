import DataSourcesView from '@/features/data-sources/components/DataSourcesView.jsx';
import { useDataSources } from '@/features/data-sources/hooks/useDataSources.js';

export default function DataSourcesDashboard() {
  const { dataSources, loading, error, checkConnection } = useDataSources();
  return <DataSourcesView dataSources={dataSources} loading={loading} error={error} onCheckSources={checkConnection} />;
}
