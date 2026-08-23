import { HttpClient } from '../request.js';

export class QuantClient extends HttpClient {
  handleRequest(config) {
    return config;
  }

  handleResponse(response) {
    return response;
  }
}

// 创建Quant连接
const request = new QuantClient({
  baseURL: 'http://127.0.0.1:8001'
});

export default request;
