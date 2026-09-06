import DatabaseView from '@/features/database/components/DatabaseView.jsx';
import { useDatabaseStatus } from '@/features/database/hooks/useDatabaseStatus.js';

export default function MongoDashboard() {
  const { databaseStatus, loading, error, refresh } = useDatabaseStatus();
  return <DatabaseView databaseStatus={databaseStatus} loading={loading} error={error} onRefresh={refresh} />;
}
