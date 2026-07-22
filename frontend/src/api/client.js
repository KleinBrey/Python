const API_BASE_URLS = [
  import.meta.env.VITE_API_BASE_URL,
  'http://127.0.0.1:8001',
].filter(Boolean);

export async function apiGet(path) {
  let lastError = null;

  for (const baseUrl of API_BASE_URLS) {
    try {
      const response = await fetch(`${baseUrl}${path}`);
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.error || '请求失败');
      }
      return payload;
    } catch (err) {
      lastError = err;
    }
  }

  throw lastError || new Error('请求失败');
}
