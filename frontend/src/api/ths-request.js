import axios from 'axios';

/**
 * 业务响应信封结构
 * @typedef {Object} ApiResponse
 * @property {number} code - 业务结果码（0 表示成功，非 0 表示业务错误）
 * @property {string} message - 结果描述
 * @property {string} request_id - 请求追踪 ID
 * @property {any} data - 业务数据容器
 */

/**
 * 自定义业务异常类
 */
export class FuyaoApiError extends Error {
  constructor(code, message, requestId) {
    super(`[Fuyao API Error ${code}]: ${message}`);
    this.name = 'FuyaoApiError';
    this.code = code;
    this.requestId = requestId;
  }
}

/**
 * 同花顺扶摇金融数据 API SDK 封装类
 */
class FuyaoClient {
  /**
   * @param {Object} options
   * @param {string} [options.baseURL='https://fuyao.aicubes.cn'] - API 基础地址
   * @param {string} [options.apiKey] - 同花顺 API Key
   * @param {number} [options.timeout=10000] - 超时时间 (ms)
   */
  constructor(options = {}) {
    this.apiKey = options.apiKey || process.env.FUYAO_TOKEN || process.env.API_KEY || '';

    this.client = axios.create({
      baseURL: options.baseURL || 'https://fuyao.aicubes.cn',
      timeout: options.timeout || 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  /**
   * 设置 / 更新 API Key
   * @param {string} apiKey 
   */
  setApiKey (apiKey) {
    this.apiKey = apiKey;
  }

  /**
   * 配置请求与响应拦截器
   */
  setupInterceptors () {
    // 1. 请求拦截器：注入 X-api-key
    this.client.interceptors.request.use(
      (config) => {
        if (this.apiKey) {
          config.headers['X-api-key'] = this.apiKey;
        } else {
          console.warn('[Fuyao SDK] 警告: 未设置 X-api-key，部分或全部接口可能无法访问 (code 2001)。');
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // 2. 响应拦截器：统一业务错误处理与数据解包
    this.client.interceptors.response.use(
      (response) => {
        const resData = response.data;

        // 判断是否符合统一信封响应结构
        if (resData && typeof resData.code !== 'undefined') {
          // code !== 0 表示业务逻辑错误 (例如 1001:缺少参数, 1002:格式错误, 2001:Key失效等)
          if (resData.code !== 0) {
            return Promise.reject(
              new FuyaoApiError(resData.code, resData.message, resData.request_id)
            );
          }
          // 成功则返回最外层的标准 response 结构
          return resData;
        }

        return resData;
      },
      (error) => {
        // 网络错误或 HTTP 状态码异常 (4xx/5xx)
        if (error.response && error.response.data) {
          const { code, message, request_id } = error.response.data;
          if (code !== undefined) {
            return Promise.reject(new FuyaoApiError(code, message, request_id));
          }
        }
        return Promise.reject(error);
      }
    );
  }

  // =========================================================================
  // 1. 价格数据 (prices) - Path: /api/a-share/prices
  // =========================================================================

  /**
   * 获取行情快照 (支持单只、多只批量或全市场分页)
   * @param {Object} [params]
   * @param {string} [params.thscodes] - 逗号分隔的代码列表，如 "600519.SH,000001.SZ"
   * @param {number} [params.limit] - 全市场分页大小
   * @param {number} [params.offset] - 全市场分页偏移量
   */
  getPricesSnapshot (params = {}) {
    return this.client.get('/api/a-share/prices/snapshot', { params });
  }

  /**
   * 获取单只标的历史 K 线数据
   * @param {Object} params
   * @param {string} params.thscode - 标的代码，如 "600519.SH"
   * @param {string} [params.period='daily'] - K线周期: daily | weekly | monthly
   * @param {string} [params.adjust='none'] - 复权类型: none | forward (前复权) | backward (后复权)
   * @param {string} [params.start] - 起始日期 YYYY-MM-DD
   * @param {string} [params.end] - 截止日期 YYYY-MM-DD
   * @param {number} [params.start_ms] - 起始时间戳 (毫秒)
   * @param {number} [params.end_ms] - 截止时间戳 (毫秒)
   */
  getPricesHistorical (params) {
    return this.client.get('/api/a-share/prices/historical', { params });
  }

  // =========================================================================
  // 2. 全市场数据导出 (market-dumps) - Path: /dump/market-dumps
  // =========================================================================

  /**
   * 获取全市场历史数据 Parquet 文件导出/下载链接
   * @param {Object} [params]
   * @param {string} [params.type] - 导出类型，如 '10y_kline' | 'recent_10d' | 'adjust_factors'
   */
  getMarketDumps (params = {}) {
    return this.client.get('/dump/market-dumps', { params });
  }

  // =========================================================================
  // 3. 标的检索与列表 - Path: /api/meta/tickers
  // =========================================================================

  /**
   * 按关键字检索 A 股、指数与基金标的
   * @param {Object} params
   * @param {string} params.q - 搜索关键词 (代码/拼音/名称)
   * @param {number} [params.limit=20] - 结果数量限制
   */
  searchTickers (params) {
    return this.client.get('/api/meta/tickers/search', { params });
  }

  /**
   * 按规范化资产类型分页获取标的代码列表
   * @param {Object} [params]
   * @param {string} [params.asset_type] - 资产类型，如 'stock' | 'index' | 'fund'
   * @param {number} [params.page=1] - 页码
   * @param {number} [params.page_size=100] - 每页数量
   */
  getTickersList (params = {}) {
    return this.client.get('/api/meta/tickers/list', { params });
  }

  /**
   * 获取 A 股交易日历
   * @param {Object} [params]
   * @param {string} [params.start] - 起始日期 YYYY-MM-DD
   * @param {string} [params.end] - 截止日期 YYYY-MM-DD
   */
  getTradingCalendar (params = {}) {
    return this.client.get('/api/a-share/calendar/trading-days', { params });
  }

  // =========================================================================
  // 4. 基金 (fund) - Path: /api/fund
  // =========================================================================

  /**
   * 获取基金基本资料与行情/净值/收益/持仓数据
   * @param {Object} params
   * @param {string} params.thscode - 基金代码，如 "000001.OF"
   * @param {string} [params.type] - 接口子类型（如 'profile' | 'holdings' | 'nav' | 'returns'）
   */
  getFundData (params) {
    return this.client.get('/api/fund', { params });
  }

  /**
   * 获取基金重仓股/持仓结构 (便捷封装)
   * @param {string} thscode - 基金代码
   * @param {Object} [extraParams]
   */
  getFundHoldings (thscode, extraParams = {}) {
    return this.client.get('/api/fund/holdings', {
      params: { thscode, ...extraParams },
    });
  }

  /**
   * 获取基金净值历史 (便捷封装)
   * @param {string} thscode - 基金代码
   * @param {Object} [extraParams]
   */
  getFundNAV (thscode, extraParams = {}) {
    return this.client.get('/api/fund/nav', {
      params: { thscode, ...extraParams },
    });
  }

  // =========================================================================
  // 5. 除复权 (corporate-actions) - Path: /api/a-share/corporate-actions
  // =========================================================================

  /**
   * 获取 A 股除复权因子事件流（分红 / 送股 / 配股）
   * @param {Object} params
   * @param {string} params.thscode - 单只标的代码 (例如 "600519.SH")
   * @param {string} [params.from] - 事件起始日期 YYYY-MM-DD
   * @param {string} [params.to] - 事件截止日期 YYYY-MM-DD
   */
  getCorporateActions (params) {
    return this.client.get('/api/a-share/corporate-actions/adjustment-factors', { params });
  }

  // =========================================================================
  // 6. 财务报表 (financials) - Path: /api/a-share/financials
  // =========================================================================

  /**
   * 获取 A 股合并利润表 (Income Statement)
   * @param {Object} params
   * @param {string} params.thscode - 标的代码，如 "600519.SH"
   * @param {string} [params.period] - 报表周期: annual (年报) | quarterly (季报)
   * @param {number} [params.limit=5] - 返回近 N 期
   */
  getIncomeStatements (params) {
    return this.client.get('/api/a-share/financials/income-statements', { params });
  }

  /**
   * 获取 A 股资产负债表 (Balance Sheet)
   * @param {Object} params
   * @param {string} params.thscode - 标的代码
   * @param {string} [params.period] - 报表周期: annual | quarterly
   * @param {number} [params.limit=5] - 返回近 N 期
   */
  getBalanceSheets (params) {
    return this.client.get('/api/a-share/financials/balance-sheets', { params });
  }

  /**
   * 获取 A 股现金流量表 (Cash Flow Statement)
   * @param {Object} params
   * @param {string} params.thscode - 标的代码
   * @param {string} [params.period] - 报表周期: annual | quarterly
   * @param {number} [params.limit=5] - 返回近 N 期
   */
  getCashFlowStatements (params) {
    return this.client.get('/api/a-share/financials/cash-flow-statements', { params });
  }
}

// 导出单例对象，同时支持 class 实例自定义创建
export const fuyao = new FuyaoClient();
export default FuyaoClient;