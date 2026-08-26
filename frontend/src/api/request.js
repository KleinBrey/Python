import axios from 'axios';

export class HttpClient {
  constructor(config = {}) {
    this.service = axios.create({
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json;charset=utf-8'
      },
      ...config
    });

    this.setupInterceptors();
  }

  setupInterceptors() {
    this.service.interceptors.request.use(
      config => this.handleRequest(config),
      error => this.handleRequestError(error)
    );

    this.service.interceptors.response.use(
      response => this.handleResponse(response),
      error => this.handleResponseError(error)
    );
  }

  handleRequest(config) {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  }

  handleRequestError(error) {
    console.error('请求发起失败:', error);
    return Promise.reject(error);
  }

  handleResponse(response) {
    return response;
  }

  handleResponseError(error) {
    if (error.response) {
      const { status } = error.response;
      const messages = {
        401: '未授权/登录过期，请重新登录',
        403: '拒绝访问',
        404: '请求的资源不存在',
        500: '服务器内部错误'
      };
      console.error(messages[status] || `请求错误: ${status}`);
    } else if (error.code === 'ECONNABORTED') {
      console.error('请求超时，请检查网络后再试');
    } else {
      console.error('网络连接异常');
    }

    return Promise.reject(error);
  }

  request(config) {
    return this.service.request(config);
  }

  get(url, params = {}, config = {}) {
    return this.service.get(url, { ...config, params });
  }

  post(url, data = {}, config = {}) {
    return this.service.post(url, data, config);
  }

  put(url, data = {}, config = {}) {
    return this.service.put(url, data, config);
  }

  patch(url, data = {}, config = {}) {
    return this.service.patch(url, data, config);
  }

  delete(url, params = {}, config = {}) {
    return this.service.delete(url, { ...config, params });
  }
}
