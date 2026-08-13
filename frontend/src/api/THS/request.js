import { HttpClient } from '../request.js'

const apiKey = import.meta.env.HITHINK_FINANCE_API_KEY?.trim() || ''

// 错误类型常量
const ERROR_TYPES = {
  PARAMETER: 'parameter',
  AUTH: 'auth',
  PERMISSION: 'permission',
  DATA: 'data',
  RATE_LIMIT: 'rate-limit',
  SERVER: 'server',
  UNKNOWN: 'unknown',
}

export const FUYAO_ERROR_MAP = {
  // 参数错误 (1xxx)
  1001: {
    type: ERROR_TYPES.PARAMETER,
    message: '缺少必填参数',
    retryable: false,
  },
  1002: {
    type: ERROR_TYPES.PARAMETER,
    message: '参数格式错误',
    retryable: false,
  },
  1003: {
    type: ERROR_TYPES.PARAMETER,
    message: '参数取值越界',
    retryable: false,
  },
  1004: { type: ERROR_TYPES.PARAMETER, message: '参数冲突', retryable: false },
  // 认证错误 (2xxx)
  2001: {
    type: ERROR_TYPES.AUTH,
    message: 'API Key 缺失或无效',
    retryable: false,
  },
  2003: {
    type: ERROR_TYPES.PERMISSION,
    message: 'API Key 无权调用该接口',
    retryable: false,
  },
  // 数据错误 (3xxx)
  3001: { type: ERROR_TYPES.DATA, message: '标的不存在', retryable: false },
  3002: { type: ERROR_TYPES.DATA, message: '数据暂未就绪', retryable: true },
  3004: {
    type: ERROR_TYPES.DATA,
    message: '当前标的类型不支持该接口',
    retryable: false,
  },
  // 限流错误 (4xxx)
  4001: {
    type: ERROR_TYPES.RATE_LIMIT,
    message: '请求过于频繁，请稍后重试',
    retryable: true,
  },
  // 服务器错误 (5xxx)
  5001: {
    type: ERROR_TYPES.SERVER,
    message: '扶摇服务内部错误',
    retryable: true,
  },
  5002: {
    type: ERROR_TYPES.SERVER,
    message: '上游服务响应超时',
    retryable: true,
  },
  5003: {
    type: ERROR_TYPES.SERVER,
    message: '上游数据源暂时不可用',
    retryable: true,
  },
}

export class FuyaoApiError extends Error {
  constructor(code, message, requestId) {
    const definition = FUYAO_ERROR_MAP[code] ?? {
      type: ERROR_TYPES.UNKNOWN,
      message: '未知业务错误',
      retryable: false,
    }

    super(message || definition.message)
    this.name = 'FuyaoApiError'
    this.code = code
    this.requestId = requestId
    this.type = definition.type
    this.retryable = definition.retryable
    this.defaultMessage = definition.message
  }
}

export class FuyaoClient extends HttpClient {
  handleRequest(config) {
    if (!apiKey) {
      throw new FuyaoApiError(2001, '未配置 HITHINK_FINANCE_API_KEY')
    }

    config.headers['X-api-key'] = apiKey
    return config
  }

  handleResponse(response) {
    const payload = super.handleResponse(response)

    // 扶摇业务错误同样返回 HTTP 200，需要通过 code 判断。
    if (payload && typeof payload.code === 'number' && payload.code !== 0) {
      throw new FuyaoApiError(payload.code, payload.message, payload.request_id)
    }

    return payload
  }
}

const request = new FuyaoClient({
  baseURL: import.meta.env.VITE_THS_API_BASE_URL || 'https://fuyao.aicubes.cn',
  timeout: 15000,
})

export const service = request.service
export default request
