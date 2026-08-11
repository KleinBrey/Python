import React, { useEffect, useMemo, useState } from 'react'
import {
  ChevronLeft,
  ChevronRight,
  FileJson2,
  ListFilter,
  Loader2,
  Play,
  Search,
  Sparkles,
} from 'lucide-react'
import { apiGet, apiPost } from '../api/client.js'
import MetricCard from '../components/MetricCard.jsx'
import StockKlineChart from '../components/TradingView/StockKlineChart.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Button } from '@/components/ui/button.jsx'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { formatValue, shortTime } from '../utils/formatters.js'

const exampleQueries = [
  '总市值大于100亿，ST股除外，科创板除外，北交所除外，最近5日涨幅大于5%，按个股热度排序',
  '今日涨幅大于5%，成交量大于过去20日平均成交量2倍，非ST股',
  '市盈率小于30，净利润连续3年增长，近20日均线多头排列',
]

const preferredColumns = [
  '股票代码',
  '股票简称',
  '最新价',
  '最新涨跌幅',
  '上市板块',
  '交易所',
]

function collectColumns(rows) {
  const keys = []
  const seen = new Set()
  rows.slice(0, 100).forEach((row) => {
    Object.keys(row).forEach((key) => {
      if (!seen.has(key)) {
        seen.add(key)
        keys.push(key)
      }
    })
  })
  return [
    ...preferredColumns.filter((key) => seen.has(key)),
    ...keys.filter((key) => !preferredColumns.includes(key)),
  ]
}

function ResultTable({ rows }) {
  const keys = useMemo(() => collectColumns(rows), [rows])
  const [pageSize, setPageSize] = useState(50)
  const [page, setPage] = useState(1)
  const pageCount = Math.max(1, Math.ceil(rows.length / pageSize))
  const currentPage = Math.min(page, pageCount)
  const visibleRows = rows.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize,
  )

  useEffect(() => {
    setPage(1)
  }, [rows.length, pageSize])

  return (
    <div className="iwencai-result-table">
      <Table
        containerClassName="iwencai-result-table-scroll"
        style={{ minWidth: Math.max(960, keys.length * 150) }}
      >
        <TableHeader>
          <TableRow>
            {keys.map((key) => (
              <TableHead
                className={key === '股票代码' ? 'sticky-code-column' : ''}
                key={key}
                style={{
                  width:
                    key.includes('名称') || key.includes('简称') ? 140 : 150,
                }}
              >
                {key}
              </TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {visibleRows.length ? (
            visibleRows.map((row, rowIndex) => (
              <TableRow
                key={`${row.股票代码 || 'stock'}-${(currentPage - 1) * pageSize + rowIndex}`}
              >
                {keys.map((key) => {
                  const value = row[key]
                  return (
                    <TableCell
                      className={key === '股票代码' ? 'sticky-code-column' : ''}
                      key={key}
                    >
                      <span
                        title={
                          value === null || value === undefined
                            ? ''
                            : String(value)
                        }
                      >
                        {formatValue(value)}
                      </span>
                    </TableCell>
                  )
                })}
              </TableRow>
            ))
          ) : (
            <TableRow>
              <TableCell
                className="table-empty-state"
                colSpan={Math.max(1, keys.length)}
              >
                没有查询到股票，请尝试简化或放宽条件
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
      <div className="table-pagination">
        <span>
          第 {currentPage} / {pageCount} 页，共 {rows.length} 条
        </span>
        <div className="table-pagination-actions">
          <label>
            每页
            <select
              aria-label="每页显示数量"
              className="shadcn-select"
              onChange={(event) => setPageSize(Number(event.target.value))}
              value={pageSize}
            >
              {[20, 50, 100].map((size) => (
                <option key={size} value={size}>
                  {size}
                </option>
              ))}
            </select>
          </label>
          <Button
            disabled={currentPage <= 1}
            onClick={() => setPage((value) => Math.max(1, value - 1))}
            size="sm"
            type="button"
            variant="outline"
          >
            <ChevronLeft size={14} />
            上一页
          </Button>
          <Button
            disabled={currentPage >= pageCount}
            onClick={() => setPage((value) => Math.min(pageCount, value + 1))}
            size="sm"
            type="button"
            variant="outline"
          >
            下一页
            <ChevronRight size={14} />
          </Button>
        </div>
      </div>
    </div>
  )
}

function StockSelectionTable({ rows, selectedStock, onSelect }) {
  return (
    <aside className="iwencai-stock-selector">
      <div className="iwencai-stock-selector-head">
        <strong>股票列表</strong>
        <span>{rows.length} 只</span>
      </div>
      <Table
        containerClassName="iwencai-stock-table-scroll"
        style={{ minWidth: 374 }}
      >
        <TableHeader>
          <TableRow>
            <TableHead style={{ width: 112 }}>代码</TableHead>
            <TableHead style={{ width: 108 }}>股票</TableHead>
            <TableHead style={{ width: 76 }}>最新价</TableHead>
            <TableHead style={{ width: 78 }}>涨跌幅</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.map((row, index) => {
            const selected = row.股票代码 === selectedStock?.股票代码
            return (
              <TableRow
                aria-selected={selected}
                data-state={selected ? 'selected' : undefined}
                key={`${row.股票代码 || 'stock'}-${index}`}
                onClick={() => onSelect(row)}
                onKeyDown={(event) => {
                  if (event.key === 'Enter' || event.key === ' ') {
                    event.preventDefault()
                    onSelect(row)
                  }
                }}
                role="button"
                tabIndex={0}
              >
                <TableCell title={String(row.股票代码 || '')}>
                  {formatValue(row.股票代码)}
                </TableCell>
                <TableCell title={String(row.股票简称 || '')}>
                  {formatValue(row.股票简称)}
                </TableCell>
                <TableCell>{formatValue(row.最新价)}</TableCell>
                <TableCell>{formatValue(row.最新涨跌幅)}</TableCell>
              </TableRow>
            )
          })}
        </TableBody>
      </Table>
    </aside>
  )
}

export default function IwencaiSelectorDashboard() {
  const [query, setQuery] = useState('')
  const [result, setResult] = useState(null)
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [selectedStock, setSelectedStock] = useState(null)
  const [klineData, setKlineData] = useState(null)
  const [klineLoading, setKlineLoading] = useState(false)
  const [klineError, setKlineError] = useState('')
  const [klinePeriod, setKlinePeriod] = useState('daily')
  const [prefetchStatus, setPrefetchStatus] = useState(null)

  useEffect(() => {
    async function loadStatus() {
      try {
        const payload = await apiGet('/api/iwencai/status')
        setStatus(payload)
        if (payload.latest) {
          setResult(payload.latest)
          setQuery(payload.latest.query || '')
        }
      } catch (err) {
        setError(err.message)
      }
    }
    loadStatus()
  }, [])

  async function submitQuery() {
    const normalized = query.trim()
    if (!normalized || loading) return
    setLoading(true)
    setError('')
    try {
      const payload = await apiPost('/api/iwencai/query', {
        query: normalized,
        pageSize: 50,
        maxPages: 100,
        timeout: 60,
      })
      setResult(payload.item)
      if (payload.item.query_rewritten) {
        setQuery(payload.item.query)
      }
      setStatus((current) => ({ ...current, latest: payload.item }))
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const rows = result?.datas || []
  const reportedCount = result?.code_count ?? rows.length
  const queryStatus = status
    ? status.configured
      ? '已配置'
      : '待配置'
    : error
      ? '后端未连接'
      : '连接中'
  const apiKeyBadge = status
    ? status.configured
      ? 'API Key 已配置'
      : 'API Key 未配置'
    : error
      ? '后端未连接'
      : '正在连接后端'

  useEffect(() => {
    if (!rows.length) {
      setPrefetchStatus(null)
      return undefined
    }
    if (status?.marketDataConfigured === false) {
      setPrefetchStatus({
        state: 'warning',
        message: '未配置扶摇 API Key，暂不预缓存日线',
      })
      return undefined
    }
    const controller = new AbortController()
    const stocks = rows.slice(0, 300).map((row) => ({
      symbol: row.股票代码,
      name: row.股票简称,
    }))

    async function prefetchHistories() {
      setPrefetchStatus({
        state: 'loading',
        message: `正在预缓存 ${stocks.length} 只股票日线`,
      })
      try {
        const payload = await apiPost(
          '/api/stocks/history/prefetch',
          { stocks, adjust: 'none', workers: 4 },
          { signal: controller.signal },
        )
        const summary = payload.item
        setPrefetchStatus({
          state: summary.failed ? 'warning' : 'success',
          message: summary.failed
            ? `已缓存 ${summary.completed} 只，${summary.failed} 只失败`
            : `已缓存 ${summary.completed} 只股票日线，点击即可显示`,
        })
      } catch (err) {
        if (err.name === 'AbortError') return
        setPrefetchStatus({
          state: 'warning',
          message: `日线预缓存失败：${err.message}`,
        })
      }
    }

    prefetchHistories()
    return () => controller.abort()
  }, [result, status?.marketDataConfigured])

  useEffect(() => {
    if (!rows.length) {
      setSelectedStock(null)
      return
    }
    if (
      !selectedStock ||
      !rows.some((row) => row.股票代码 === selectedStock.股票代码)
    ) {
      setSelectedStock(rows[0])
    }
  }, [rows, selectedStock])

  useEffect(() => {
    const controller = new AbortController()

    async function loadKline() {
      if (!selectedStock?.股票代码) return
      if (status?.marketDataConfigured === false) {
        setKlineData(null)
        setKlineLoading(false)
        setKlineError('未配置 HITHINK_FINANCE_API_KEY，无法读取扶摇历史行情')
        return
      }
      setKlineLoading(true)
      setKlineError('')
      try {
        const symbol = String(selectedStock.股票代码).replace(
          /\.(SZ|SH|BJ)$/i,
          '',
        )
        const name = String(selectedStock.股票简称 || '')
        const payload = await apiGet(
          `/api/stocks/history?symbol=${encodeURIComponent(symbol)}&name=${encodeURIComponent(name)}&period=${klinePeriod}`,
          { signal: controller.signal },
        )
        setKlineData(payload.item)
      } catch (err) {
        if (err.name === 'AbortError') return
        setKlineData(null)
        setKlineError(err.message)
      } finally {
        if (!controller.signal.aborted) setKlineLoading(false)
      }
    }
    loadKline()
    return () => controller.abort()
  }, [selectedStock, klinePeriod, status?.marketDataConfigured])

  return (
    <div className="dashboard-content iwencai-dashboard">
      <section className="metric-grid" aria-label="问财查询概览">
        <MetricCard
          label="符合条件"
          value={reportedCount}
          note="同花顺问财返回的股票总数"
          icon={ListFilter}
          tone="teal"
        />
        <MetricCard
          label="已获取"
          value={rows.length}
          note="当前已完整获取的结果行数"
          icon={FileJson2}
          tone="indigo"
        />
        <MetricCard
          label="分页数量"
          value={result?.pages_fetched ?? '-'}
          note="自动分页获取，无需手工翻页"
          icon={Search}
          tone="rose"
        />
        <MetricCard
          label="查询状态"
          value={queryStatus}
          note="API Key 仅保存在本机后端"
          icon={Sparkles}
          tone="amber"
        />
      </section>

      <section className="panel iwencai-query-panel">
        <div className="panel-header">
          <div>
            <h2>自然语言问财选股</h2>
            <span>写下行情、技术、财务或行业条件，系统会自动获取全部分页</span>
          </div>
          <Badge
            variant={
              status?.configured ? 'success' : status ? 'warning' : 'secondary'
            }
          >
            {apiKeyBadge}
          </Badge>
        </div>
        <div className="iwencai-query-body">
          <div className="iwencai-textarea-field">
            <Textarea
              aria-label="问财查询条件"
              maxLength={2000}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="例如：总市值大于100亿，非ST，最近5日涨幅大于5%，按个股热度排序"
              rows={5}
              value={query}
            />
            <span>{query.length} / 2000</span>
          </div>
          <div className="iwencai-examples">
            <span>示例条件</span>
            {exampleQueries.map((example, index) => (
              <Button
                key={example}
                type="button"
                onClick={() => setQuery(example)}
                size="sm"
                variant="outline"
              >
                示例 {index + 1}
              </Button>
            ))}
          </div>
          <div className="iwencai-query-actions">
            <p>
              数据来源：同花顺问财。查询结果是研究候选集合，不构成投资建议。
            </p>
            <Button
              onClick={submitQuery}
              size="lg"
              type="button"
              disabled={!query.trim() || loading || !status?.configured}
            >
              {loading ? (
                <Loader2 className="spin" size={16} />
              ) : (
                <Play size={16} />
              )}
              {loading ? '正在查询并获取全部分页' : '开始选股'}
            </Button>
          </div>
        </div>
      </section>

      {!status?.configured && status ? (
        <div className="notice">
          未配置 IWENCAI_API_KEY，请先在环境变量或 ~/.zshrc 中配置后重启后端。
        </div>
      ) : null}
      {error ? <div className="notice">{error}</div> : null}

      <section className="panel iwencai-result-panel">
        <div className="panel-header">
          <div>
            <h2>选股结果</h2>
            <span>
              {result
                ? `查询于 ${shortTime(result.fetched_at)}，共 ${formatValue(rows.length)} 行`
                : '输入查询条件后返回股票列表'}
            </span>
          </div>
          <div className="panel-header-badges">
            {prefetchStatus ? (
              <Badge
                variant={
                  prefetchStatus.state === 'success'
                    ? 'success'
                    : prefetchStatus.state === 'warning'
                      ? 'warning'
                      : 'secondary'
                }
              >
                {prefetchStatus.state === 'loading' ? (
                  <Loader2 className="spin" size={13} />
                ) : null}
                {prefetchStatus.message}
              </Badge>
            ) : null}
            {result?.source ? (
              <Badge variant="secondary">{result.source}</Badge>
            ) : null}
          </div>
        </div>
        {result?.query ? (
          <div className="iwencai-result-query">
            <strong>查询条件</strong>
            <span>{result.query}</span>
          </div>
        ) : null}
        {result?.query_rewritten ? (
          <div className="iwencai-result-query">
            <strong>系统改写</strong>
            <span>{(result.normalization_notes || []).join('；')}</span>
          </div>
        ) : null}
        <div className="iwencai-result-workspace">
          <StockSelectionTable
            rows={rows}
            selectedStock={selectedStock}
            onSelect={setSelectedStock}
          />
          <StockKlineChart
            data={klineData}
            error={klineError}
            loading={klineLoading}
            onPeriodChange={setKlinePeriod}
            period={klinePeriod}
            stock={selectedStock}
          />
        </div>
        <div className="iwencai-full-result-head">
          <strong>完整查询数据</strong>
          <span>横向滚动查看问财返回的全部指标</span>
        </div>
        <ResultTable rows={rows} />
      </section>
    </div>
  )
}
