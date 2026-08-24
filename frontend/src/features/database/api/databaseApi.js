import { apiGet } from '@/api/client.js';

export function getDatabaseStatus({ signal } = {}) {
  return apiGet('/api/database', { signal });
}
