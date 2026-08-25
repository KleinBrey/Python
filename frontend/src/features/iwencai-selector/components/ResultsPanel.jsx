import { Loader2 } from 'lucide-react';

import StockKlineChart from '@/components/TradingView/StockKlineChart.jsx';
import { Badge } from '@/shadcn/components/ui/badge.jsx';
import { formatValue, shortTime } from '@/utils/formatters.js';
import ResultTable from './ResultTable.jsx';
import StockSelectionTable from './StockSelectionTable.jsx';

export default function ResultsPanel({ result, rows, marketData }) {
  const { selectedStock, setSelectedStock, klineData, klineLoading, klineError, klinePeriod, setKlinePeriod, prefetchStatus } = marketData;
  return (
    <section className="panel iwencai-result-panel">
      <div className="panel-header">
        <div><h2>选股结果</h2><span>{result ? `查询于 ${shortTime(result.fetched_at)}，共 ${formatValue(rows.length)} 行` : '输入查询条件后返回股票列表'}</span></div>
        <div className="panel-header-badges">
          {prefetchStatus ? <Badge variant={prefetchStatus.state === 'success' ? 'success' : prefetchStatus.state === 'warning' ? 'warning' : 'secondary'}>{prefetchStatus.state === 'loading' ? <Loader2 className="spin" size={13} /> : null}{prefetchStatus.message}</Badge> : null}
          {result?.source ? <Badge variant="secondary">{result.source}</Badge> : null}
        </div>
      </div>
      {result?.query ? <div className="iwencai-result-query"><strong>查询条件</strong><span>{result.query}</span></div> : null}
      {result?.query_rewritten ? <div className="iwencai-result-query"><strong>系统改写</strong><span>{(result.normalization_notes || []).join('；')}</span></div> : null}
      <div className="iwencai-result-workspace">
        <StockSelectionTable rows={rows} selectedStock={selectedStock} onSelect={setSelectedStock} />
        <StockKlineChart data={klineData} error={klineError} loading={klineLoading} onPeriodChange={setKlinePeriod} period={klinePeriod} stock={selectedStock} />
      </div>
      <div className="iwencai-full-result-head"><strong>完整查询数据</strong><span>横向滚动查看问财返回的全部指标</span></div>
      <ResultTable rows={rows} />
    </section>
  );
}
