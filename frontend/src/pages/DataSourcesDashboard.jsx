import DataSourcesView from '@/features/data-sources/components/DataSourcesView.jsx';
import { useDataSources } from '@/features/data-sources/hooks/useDataSources.js';

export default function DataSourcesDashboard() {
  const syncState = useDataSources();
  return <DataSourcesView {...syncState} />;
}
