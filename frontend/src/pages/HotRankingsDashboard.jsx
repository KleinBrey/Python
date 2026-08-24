import { React, useState, useRef, useEffect } from 'react';
import { Database, LayoutDashboard, Loader2, RefreshCcw, Search, Table2, TrendingUp } from 'lucide-react';
import { Button } from '@/components/ui/button.jsx';
import MetricCard from '../components/MetricCard.jsx';
import { formatValue, latestRefreshTime, rankingScore, shortTime, trendClass } from '../utils/formatters.js';
import {
  getPriceSnapshotApi,
  getSkyRocketListApi,
  getHotStockListApi,
  getHistoricalPriceApi
} from '../api/hithink/api.js';
import { getStocksListApi, updateStocksListApi, getDailyBarsApi } from '../api/quantide/api.js';
import moment from 'moment';
import { AgGridProvider, AgGridReact } from 'ag-grid-react';
import { AllCommunityModule, colorSchemeDark, themeQuartz } from 'ag-grid-community';
import StockKlineChart from '../components/TradingView/StockKlineChart.jsx';

const themeDarkBlue = themeQuartz.withPart(colorSchemeDark).withParams({
  backgroundColor: '#09090b'
  // accentColor: 'red',
});

function AgGridTable({ rowData, colDefs, handleRowClick }) {
  const modules = [AllCommunityModule];

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
  );
}

function RankingTable({ activeRanking, onRefreshRanking, refreshingId, refreshingAll }) {
  const [selectedStock, setSelectedStock] = useState({
    name: '东方财富',
    code: '453456.SZ'
  });
  const [klineData, setKlineData] = useState(null);
  const [klineLoading, setKlineLoading] = useState(false);
  const [klineError, setKlineError] = useState('');
  const [klinePeriod, setKlinePeriod] = useState('daily');
  const [prefetchStatus, setPrefetchStatus] = useState(null);

  function transformStockData(itemList) {
    if (!Array.isArray(itemList)) return [];

    return itemList.map(item => ({
      date: moment(item.date_ms).format('YYYY-MM-DD'),
      open: Number(Number(item.open_price).toFixed(2)),
      high: Number(Number(item.high_price).toFixed(2)),
      low: Number(Number(item.low_price).toFixed(2)),
      close: Number(Number(item.close_price).toFixed(2)),
      volume: Number(item.volume)
    }));
  }

  const getStockHistoryData = async thscode => {
    const res = await getHistoricalPriceApi({
      thscode: thscode,
      interval: '1d',
      start: moment().subtract(1, 'year').valueOf(),
      end: moment().valueOf()
    });
    return res;
  };

  const updateStocksList = async () => {
    try {
      const res = await updateStocksListApi();
      console.log(res, '更新数据库Stocks数据');
    } catch (error) {
      console.error('更新数据库Stocks数据失败', error);
    }
  };

  const getStockDailyBars = async () => {
    try {
      const res = await getDailyBarsApi({
        symbol: '600519',
        start_date: '2026-01-01',
        end_date: '2026-08-17'
      });
      console.log(res);
    } catch (error) {
      console.error('更新数据库Stocks数据失败', error);
    }
  };

  // 行单击事件处理函数
  const handleRowClick = async event => {
    const value = await getStockHistoryData(event.data.thscode);
    setKlineData({
      dataSource: '同花顺 HiThink',
      adjustLabel: '前复权',
      rows: transformStockData(value.data.item)
    });
    console.log(value);
  };

  // Column Definitions: Defines the columns to be displayed.
  const colDefs = useRef([
    { headerName: '排名', field: 'rank', flex: 1 },
    { headerName: '股票', field: 'name', flex: 1 },
    { headerName: '代码', field: 'thscode', flex: 1 },
    { headerName: '热度', field: 'heat', flex: 1 }
  ]);

  return (
    <section className="panel table-panel">
      <div className="panel-header">
        <div>
          <h2>{activeRanking?.title || '热榜详情'}</h2>
          <span>
            {moment(activeRanking?.timestamp).format('YYYY-MM-DD HH:mm:ss') || '-'} · {'5分钟前'}
          </span>
        </div>
        <Button
          type="button"
          className="ghost-button"
          variant="outline"
          onClick={() => onRefreshRanking(activeRanking?.id)}
          disabled={!activeRanking || refreshingId === activeRanking.id || refreshingAll}
        >
          {refreshingId === activeRanking?.id ? <Loader2 className="spin" size={15} /> : <RefreshCcw size={15} />}
          <span>{refreshingId === activeRanking?.id ? '更新中' : '刷新当前'}</span>
        </Button>
        <Button type="button" className="ghost-button" variant="outline" onClick={() => updateStocksList()}>
          <span>更新数据库Stocks数据</span>
        </Button>

        <Button type="button" className="ghost-button" variant="outline" onClick={() => getStockDailyBars()}>
          <span>股票历史数据</span>
        </Button>
      </div>

      <div className="table-wrap">
        <AgGridTable rowData={activeRanking?.rows || []} colDefs={colDefs.current} handleRowClick={handleRowClick} />
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
  );
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
  onRefreshRanking
}) {
  // 重复请求锁
  const fetchedLock = useRef(false);

  const topRanking = activeRanking?.rows?.[0];

  const [users, setUsers] = useState([]);
  const [loadingA, setLoading] = useState(false);

  const [hotStockList, setHotStockList] = useState({
    title: '同花顺热榜',
    timestamp: Date.now(),
    rows: []
  });

  // 1. 获取列表示例 (GET)
  const getPriceSnapshot = async codes => {
    try {
      const res = await getPriceSnapshotApi({ thscodes: codes });
      console.log(res.data);
    } catch (error) {
      console.error('获取行情快照失败', error);
    } finally {
    }
  };

  const getStocksList = async () => {
    try {
      const res = await getStocksListApi();
      console.log(res, '数据库Stocks数据');
    } catch (error) {
      console.error('获取数据库Stocks数据失败', error);
    }
  };

  const getSkyRocketList = async () => {
    const res = await getSkyRocketListApi('hour');
    console.log(res.data);
  };

  const getHotStockList = async () => {
    const hotStock = await getHotStockListApi('hour');
    const priceSnapshots = await getPriceSnapshot(hotStock.data.item.map(item => item.thscode).join(','));

    setHotStockList(prev => ({
      ...prev, // 保留原有的 title 等其他属性
      timestamp: hotStock.data.timestamp, // 更新时间戳（毫秒）
      rows: hotStock.data.item // 更新列表数据
    }));
    console.log(hotStockList, priceSnapshots);
  };

  useEffect(() => {
    // fetchUsers();
    // getSkyRocketList()
    getStocksList();
    getHotStockList();
  }, []);

  return (
    <div className="dashboard-content">
      <RankingTable
        activeRanking={hotStockList}
        onRefreshRanking={onRefreshRanking}
        refreshingId={refreshingId}
        refreshingAll={refreshingAll}
      />
    </div>
  );
}
