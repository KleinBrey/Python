import { apiGet } from '@/api/client.js';

export function getDataSources({ check = false, signal } = {}) {
  return apiGet(`/api/data-sources?check=${check ? 'true' : 'false'}`, { signal });
}
