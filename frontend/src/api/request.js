import axios from 'axios';

// 1. 设置 BaseURL（
const baseURL = 'https://fuyao.aicubes.cn/api'
const apiKey = import.meta.env.HITHINK_FINANCE_API_KEY?.trim() || ''

// 2. 创建 Axios 实例
const service = axios.create({
  baseURL,
  timeout: 10000, // 超时时间（毫秒）
  headers: {
    'Content-Type': 'application/json;charset=utf-8',
  },
});

// 3. 请求拦截器 (Request Interceptor)
service.interceptors.request.use(
  (config) => {
    // 可以在这里统一添加 Token
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    if (apiKey) {
      config.headers['X-api-key'] = apiKey;
    } else {
      console.warn('未配置 HITHINK_FINANCE_API_KEY，扶摇 API 请求可能失败');
    }
    return config;
  },
  (error) => {
    console.error('请求发起失败:', error);
    return Promise.reject(error);
  }
);

// 4. 响应拦截器 (Response Interceptor)
service.interceptors.response.use(
  (response) => {
    // 解包数据：直接返回 res.data，组件中调用时少写一层 .data
    return response.data;
  },
  (error) => {
    // 统一处理 HTTP 状态码错误
    if (error.response) {
      const { status } = error.response;
      switch (status) {
        case 401:
          console.error('未授权/登录过期，请重新登录');
          // 可在此处跳转至登录页：window.location.href = '/login';
          break;
        case 403:
          console.error('拒绝访问');
          break;
        case 404:
          console.error('请求的资源不存在');
          break;
        case 500:
          console.error('服务器内部错误');
          break;
        default:
          console.error(`请求错误: ${status}`);
      }
    } else if (error.message.includes('timeout')) {
      console.error('请求超时，请检查网络后再试');
    } else {
      console.error('网络连接异常');
    }

    return Promise.reject(error);
  }
);

// 5. 封装基础请求方法 (GET, POST, PUT, DELETE)
const request = {
  /**
   * GET 请求
   * @param {string} url 请求地址
   * @param {object} params URL 查询参数
   * @param {object} config 额外的 axios 配置
   */
  get (url, params = {}, config = {}) {
    return service.get(url, { params, ...config });
  },

  /**
   * POST 请求
   * @param {string} url 请求地址
   * @param {object} data 请求体数据
   * @param {object} config 额外的 axios 配置
   */
  post (url, data = {}, config = {}) {
    return service.post(url, data, config);
  },

  /**
   * PUT 请求
   * @param {string} url 请求地址
   * @param {object} data 请求体数据
   * @param {object} config 额外的 axios 配置
   */
  put (url, data = {}, config = {}) {
    return service.put(url, data, config);
  },

  /**
   * DELETE 请求
   * @param {string} url 请求地址
   * @param {object} params URL 查询参数/Path参数
   * @param {object} config 额外的 axios 配置
   */
  delete (url, params = {}, config = {}) {
    return service.delete(url, { params, ...config });
  },
};

export default request;
