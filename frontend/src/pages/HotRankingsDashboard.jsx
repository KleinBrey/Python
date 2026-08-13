import { React, useState, useRef, useEffect } from 'react'
import {
  Database,
  LayoutDashboard,
  Loader2,
  RefreshCcw,
  Search,
  Table2,
  TrendingUp,
} from 'lucide-react'
import { Button } from '@/components/ui/button.jsx'
import MetricCard from '../components/MetricCard.jsx'
import {
  formatValue,
  latestRefreshTime,
  rankingScore,
  shortTime,
  trendClass,
} from '../utils/formatters.js'
import {
  getPriceSnapshotApi,
  getSkyRocketListApi,
  getHotStockListApi,
  getHistoricalPriceApi,
} from '../api/hot-rank-api.js'
import moment from 'moment'
import { AgGridProvider, AgGridReact } from 'ag-grid-react'
import {
  AllCommunityModule,
  colorSchemeDark,
  themeQuartz,
} from 'ag-grid-community'
import StockKlineChart from '../components/TradingView/StockKlineChart.jsx'

const themeDarkBlue = themeQuartz.withPart(colorSchemeDark).withParams({
  backgroundColor: '#09090b',
  // accentColor: 'red',
})

function SourceCards({ sourceStats }) {
  return (
    <section className="source-grid" aria-label="数据源统计">
      {sourceStats.map((item) => (
        <article key={item.source} className="source-card">
          <span>{item.source}</span>
          <strong>{item.count} 榜</strong>
          <em>{formatValue(item.rows)} 条记录</em>
        </article>
      ))}
      {!sourceStats.length ? (
        <article className="source-card">
          <span>暂无来源</span>
          <strong>-</strong>
          <em>等待缓存或刷新</em>
        </article>
      ) : null}
    </section>
  )
}

function RankingChart({ ranking }) {
  const rows = (ranking?.rows || []).slice(0, 10)
  const values = rows.map((row) => Math.abs(Number(rankingScore(row))) || 0)
  const max = Math.max(...values, 1)

  return (
    <section className="panel chart-panel">
      <div className="panel-header">
        <div>
          <h2>榜单走势</h2>
          <span>{ranking?.title || '选择一个榜单'}</span>
        </div>
        <div className="segmented-control" aria-label="时间范围">
          <Button type="button" size="sm" variant="ghost">
            今日
          </Button>
          <Button type="button" size="sm" variant="ghost" className="active">
            当前
          </Button>
          <Button type="button" size="sm" variant="ghost">
            缓存
          </Button>
        </div>
      </div>

      <div className="bar-chart" aria-label="前十排名条形图">
        {rows.map((row, index) => {
          const score = Math.abs(Number(rankingScore(row))) || 0
          const width = Math.max(8, Math.round((score / max) * 100))
          return (
            <div
              className="bar-row"
              key={`${ranking.id}-bar-${row.rank}-${row.code || row.name}`}
            >
              <span>{String(index + 1).padStart(2, '0')}</span>
              <strong>{row.name || row.code || '-'}</strong>
              <div className="bar-track">
                <i style={{ width: `${width}%` }} />
              </div>
              <em>{formatValue(rankingScore(row))}</em>
            </div>
          )
        })}
        {!rows.length ? <div className="empty-state">暂无图表数据</div> : null}
      </div>
    </section>
  )
}

function RankingCards({
  rankings,
  activeRanking,
  onSelectRanking,
  onRefreshRanking,
  refreshingId,
  refreshingAll,
}) {
  return (
    <section className="panel rankings-panel">
      <div className="panel-header">
        <div>
          <h2>全部热榜</h2>
          <span>{rankings.length} 个榜单</span>
        </div>
        <Table2 size={18} />
      </div>

      <div className="ranking-list">
        {rankings.map((ranking) => (
          <article
            key={ranking.id}
            className={`ranking-card ${activeRanking?.id === ranking.id ? 'selected' : ''}`}
            onClick={() => onSelectRanking(ranking.id)}
          >
            <div className="ranking-card-head">
              <div>
                <span>{ranking.source}</span>
                <h3>{ranking.title}</h3>
              </div>
              <Button
                type="button"
                className="icon-button"
                size="icon"
                variant="outline"
                onClick={(event) => {
                  event.stopPropagation()
                  onRefreshRanking(ranking.id)
                }}
                disabled={refreshingId === ranking.id || refreshingAll}
                title="刷新榜单"
              >
                {refreshingId === ranking.id ? (
                  <Loader2 className="spin" size={15} />
                ) : (
                  <RefreshCcw size={15} />
                )}
              </Button>
            </div>

            {ranking.error ? (
              <div className="inline-error">{ranking.error}</div>
            ) : null}

            <ol className="mini-rank">
              {(ranking.rows || []).slice(0, 4).map((row) => (
                <li key={`${ranking.id}-${row.rank}-${row.code || row.name}`}>
                  <span>{row.rank}</span>
                  <strong>{row.name || row.code || '-'}</strong>
                  <em>{formatValue(rankingScore(row))}</em>
                </li>
              ))}
              {!ranking.rows?.length ? (
                <li className="empty-line">暂无缓存</li>
              ) : null}
            </ol>

            <footer>
              <span>{formatValue(ranking.rowCount)} 条</span>
              <span>{shortTime(ranking.updatedAt)}</span>
            </footer>
          </article>
        ))}
      </div>
    </section>
  )
}

function AgGridTable({ rowData, colDefs, handleRowClick }) {
  const modules = [AllCommunityModule]

  return (
    <div className="ag-grid-container">
      <AgGridProvider modules={modules}>
        <div style={{ height: '100%', width: '100%' }}>
          <AgGridReact
            theme={themeDarkBlue}
            rowData={rowData}
            columnDefs={colDefs}
            defaultColDef={{ resizable: true, sortable: true }}
            onRowClicked={handleRowClick} // 绑定行单击事件
          />
        </div>
      </AgGridProvider>
    </div>
  )
}

function RankingTable({
  activeRanking,
  onRefreshRanking,
  refreshingId,
  refreshingAll,
}) {
  const [selectedStock, setSelectedStock] = useState({
    name: '东方财富',
    code: '453456.SZ',
  })
  const [klineData, setKlineData] = useState(null)
  const [klineLoading, setKlineLoading] = useState(false)
  const [klineError, setKlineError] = useState('')
  const [klinePeriod, setKlinePeriod] = useState('daily')
  const [prefetchStatus, setPrefetchStatus] = useState(null)

  function transformStockData(itemList) {
    if (!Array.isArray(itemList)) return []

    return itemList.map((item) => ({
      date: moment(item.date_ms).format('YYYY-MM-DD'),
      open: Number(Number(item.open_price).toFixed(2)),
      high: Number(Number(item.high_price).toFixed(2)),
      low: Number(Number(item.low_price).toFixed(2)),
      close: Number(Number(item.close_price).toFixed(2)),
      volume: Number(item.volume),
    }))
  }

  const getStockHistoryData = async (thscode) => {
    const res = await getHistoricalPriceApi({
      thscode: thscode,
      interval: '1d',
      start: moment().subtract(1, 'year').valueOf(),
      end: moment().valueOf(),
    })
    return res
  }

  // 行单击事件处理函数
  const handleRowClick = async (event) => {
    const value = await getStockHistoryData(event.data.thscode)
    setKlineData({
      dataSource: '同花顺扶摇',
      adjustLabel: '前复权',
      rows: transformStockData(value.data.item),
    })
    console.log(value)
  }

  // Column Definitions: Defines the columns to be displayed.
  const colDefs = useRef([
    { headerName: '排名', field: 'rank', flex: 1 },
    { headerName: '股票', field: 'name', flex: 1 },
    { headerName: '代码', field: 'thscode', flex: 1 },
    { headerName: '热度', field: 'heat', flex: 1 },
  ])

  return (
    <section className="panel table-panel">
      <div className="panel-header">
        <div>
          <h2>{activeRanking?.title || '热榜详情'}</h2>
          <span>
            {moment(activeRanking?.timestamp).format('YYYY-MM-DD HH:mm:ss') ||
              '-'}{' '}
            · {'5分钟前'}
          </span>
        </div>
        <Button
          type="button"
          className="ghost-button"
          variant="outline"
          onClick={() => onRefreshRanking(activeRanking?.id)}
          disabled={
            !activeRanking || refreshingId === activeRanking.id || refreshingAll
          }
        >
          {refreshingId === activeRanking?.id ? (
            <Loader2 className="spin" size={15} />
          ) : (
            <RefreshCcw size={15} />
          )}
          <span>
            {refreshingId === activeRanking?.id ? '更新中' : '刷新当前'}
          </span>
        </Button>
      </div>

      <div className="table-wrap">
        <AgGridTable
          rowData={activeRanking?.rows || []}
          colDefs={colDefs.current}
          handleRowClick={handleRowClick}
        />
        <StockKlineChart
          loading={klineLoading}
          data={klineData}
          error={klineError}
          period={klinePeriod}
          onPeriodChange={setKlinePeriod}
          stock={selectedStock}
        />
      </div>
    </section>
  )
}

export default function HotRankingsDashboard({
  summary,
  rankings,
  activeRanking,
  loading,
  error,
  sourceStats,
  refreshingAll,
  refreshingId,
  onLoadCache,
  onSelectRanking,
  onRefreshRanking,
}) {
  // 重复请求锁
  const fetchedLock = useRef(false)

  const topRanking = activeRanking?.rows?.[0]

  const [users, setUsers] = useState([])
  const [loadingA, setLoading] = useState(false)

  const [hotStockList, setHotStockList] = useState({
    title: '同花顺热榜',
    timestamp: Date.now(),
    rows: [],
  })

  // 1. 获取列表示例 (GET)
  const getPriceSnapshot = async (codes) => {
    try {
      const res = await getPriceSnapshotApi(codes)
      console.log(res.data)
    } catch (error) {
      console.error('获取行情快照失败', error)
    } finally {
    }
  }

  const getSkyRocketList = async () => {
    const res = await getSkyRocketListApi('hour')
    console.log(res.data)
  }

  const getHotStockList = async () => {
    const hotStock = await getHotStockListApi('hour')
    const priceSnapshots = await getPriceSnapshot(
      hotStock.data.item.map((item) => item.thscode).join(','),
    )

    setHotStockList((prev) => ({
      ...prev, // 保留原有的 title 等其他属性
      timestamp: hotStock.data.timestamp, // 更新时间戳（毫秒）
      rows: hotStock.data.item, // 更新列表数据
    }))
    console.log(hotStockList, priceSnapshots)
  }

  useEffect(() => {
    // fetchUsers();
    // getSkyRocketList()
    getHotStockList()
  }, [])

  return (
    <div className="dashboard-content">
      {/* <section className="metric-grid" aria-label="热度概览">
        <MetricCard
          label="数据源"
          value={summary?.dataSource || '同花顺扶摇 Financial API'}
          note="当前后端数据入口"
          icon={Database}
          tone="teal"
        />
        <MetricCard
          label="已配置榜单"
          value={summary?.configuredRankingCount ?? rankings.length}
          note={loading ? '正在读取' : `${rankings.length} 个已返回`}
          icon={LayoutDashboard}
          tone="indigo"
        />
        <MetricCard
          label="缓存榜单"
          value={summary?.hotRankingCount}
          note="MongoDB 中的热榜快照"
          icon={Table2}
          tone="rose"
        />
        <MetricCard
          label="榜首股票"
          value={topRanking?.name || topRanking?.code || '-'}
          note={`最近刷新 ${latestRefreshTime(rankings)}`}
          icon={TrendingUp}
          tone="amber"
        />
      </section> */}

      {/* {error ? (
        <div className="notice">
          <span>{error}</span>
          <Button type="button" className="ghost-button" onClick={onLoadCache} variant="outline">
            <Search size={15} />
            <span>读取缓存</span>
          </Button>
        </div>
      ) : null}

      <SourceCards sourceStats={sourceStats} /> */}

      {/* <section className="dashboard-grid">
        <RankingChart ranking={activeRanking} />
        <RankingCards
          rankings={rankings}
          activeRanking={activeRanking}
          onSelectRanking={onSelectRanking}
          onRefreshRanking={onRefreshRanking}
          refreshingId={refreshingId}
          refreshingAll={refreshingAll}
        />
      </section> */}

      <RankingTable
        activeRanking={hotStockList}
        onRefreshRanking={onRefreshRanking}
        refreshingId={refreshingId}
        refreshingAll={refreshingAll}
      />
    </div>
  )
}
