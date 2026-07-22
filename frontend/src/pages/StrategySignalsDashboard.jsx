import React, { useEffect, useMemo, useState } from 'react';
import { Braces, FileSearch, Layers3, ListChecks, Loader2, RefreshCcw } from 'lucide-react';
import { Button } from '@/components/ui/button.jsx';
import { apiGet } from '../api/client.js';
import MetricCard from '../components/MetricCard.jsx';
import StatusBadge from '../components/StatusBadge.jsx';
import { formatValue, shortTime, trendClass } from '../utils/formatters.js';

const sourceIcons = {
  iwencai: FileSearch,
  handwritten: Braces,
};

function SourceCard({ source }) {
  const Icon = sourceIcons[source.id] || Layers3;
  const detail = source.id === 'iwencai'
    ? source.metadata?.resultFile
    : (source.metadata?.strategies || []).map((item) => item.name).join('、');

  return (
    <article className="strategy-source-card">
      <div className="strategy-source-head">
        <div className="strategy-source-title">
          <span className={`strategy-source-icon ${source.id}`}><Icon size={18} /></span>
          <div>
            <h3>{source.name}</h3>
            <p>{source.description}</p>
          </div>
        </div>
        <StatusBadge status={source.status} />
      </div>
      <div className="strategy-source-meta">
        <div><span>股票数量</span><strong>{formatValue(source.stockCount)}</strong></div>
        <div><span>更新时间</span><strong>{shortTime(source.updatedAt)}</strong></div>
      </div>
      {detail ? <p className="strategy-source-detail" title={detail}>{detail}</p> : null}
      {source.error ? <div className="inline-error">{source.error}</div> : null}
    </article>
  );
}

function StockTable({ stocks }) {
  return (
    <section className="panel table-panel strategy-table-panel">
      <div className="panel-header">
        <div>
          <h2>策略股票列表</h2>
          <span>所有来源统一为相同字段，重复命中会保留来源信息</span>
        </div>
        <ListChecks size={19} />
      </div>
      <div className="table-wrap">
        <table className="strategy-table">
          <thead>
            <tr>
              <th>股票</th>
              <th>代码</th>
              <th>市场</th>
              <th>策略来源</th>
              <th>命中策略</th>
              <th>最新价</th>
              <th>涨跌幅</th>
              <th>入选时间</th>
            </tr>
          </thead>
          <tbody>
            {stocks.map((stock) => {
              const change = stock.metrics?.最新涨跌幅 ?? stock.metrics?.涨跌幅;
              return (
                <tr key={`${stock.source_id}-${stock.strategy_id}-${stock.code}`}>
                  <td><strong>{stock.name || '-'}</strong></td>
                  <td>{stock.code}</td>
                  <td>{stock.market || '-'}</td>
                  <td>{stock.source_name}</td>
                  <td className="strategy-name-cell" title={stock.strategy_name}>{stock.strategy_name}</td>
                  <td>{formatValue(stock.metrics?.最新价 ?? stock.metrics?.收盘价)}</td>
                  <td className={trendClass(change)}>{formatValue(change)}</td>
                  <td>{shortTime(stock.selected_at)}</td>
                </tr>
              );
            })}
            {!stocks.length ? (
              <tr><td colSpan="8" className="empty">当前来源暂无策略股票</td></tr>
            ) : null}
          </tbody>
        </table>
      </div>
    </section>
  );
}

export default function StrategySignalsDashboard() {
  const [sources, setSources] = useState([]);
  const [stocks, setStocks] = useState([]);
  const [activeSource, setActiveSource] = useState('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  async function loadStocks(sourceId = activeSource) {
    setLoading(true);
    setError('');
    try {
      const payload = await apiGet(`/api/strategy-stocks?source=${sourceId}&limit=1000`);
      setSources(payload.sources || []);
      setStocks(payload.items || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadStocks('all');
  }, []);

  const sourceCountById = useMemo(
    () => Object.fromEntries(sources.map((source) => [source.id, source.stockCount || 0])),
    [sources],
  );

  function selectSource(sourceId) {
    setActiveSource(sourceId);
    loadStocks(sourceId);
  }

  return (
    <div className="dashboard-content strategy-dashboard">
      <section className="metric-grid" aria-label="策略来源概览">
        <MetricCard label="策略来源" value={sources.length || 2} note="问财选股 + Python 手写策略" icon={Layers3} tone="indigo" />
        <MetricCard label="股票记录" value={stocks.length} note="当前筛选来源返回的记录" icon={ListChecks} tone="teal" />
        <MetricCard label="问财选股" value={sourceCountById.iwencai ?? '-'} note="读取最新问财导出结果" icon={FileSearch} tone="rose" />
        <MetricCard label="手写策略" value={sourceCountById.handwritten ?? '-'} note="项目内 Python 策略结果" icon={Braces} tone="amber" />
      </section>

      <section className="strategy-toolbar">
        <div className="strategy-source-filter" aria-label="策略来源筛选">
          {[
            ['all', '全部来源'],
            ['iwencai', '同花顺问财'],
            ['handwritten', '手写策略'],
          ].map(([id, label]) => (
            <Button
              key={id}
              type="button"
              className={activeSource === id ? 'active' : ''}
              onClick={() => selectSource(id)}
              disabled={loading}
              size="sm"
              variant="ghost"
            >
              {label}
            </Button>
          ))}
        </div>
        <Button type="button" className="ghost-button" onClick={() => loadStocks()} disabled={loading} variant="outline">
          {loading ? <Loader2 className="spin" size={15} /> : <RefreshCcw size={15} />}
          重新读取
        </Button>
      </section>

      {error ? <div className="notice">{error}</div> : null}

      <section className="strategy-source-grid">
        {sources.map((source) => <SourceCard key={source.id} source={source} />)}
      </section>

      <StockTable stocks={stocks} />
    </div>
  );
}
