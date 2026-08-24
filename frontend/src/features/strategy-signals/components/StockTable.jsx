import { ListChecks } from 'lucide-react';

import { formatValue, shortTime, trendClass } from '@/utils/formatters.js';

export default function StockTable({ stocks }) {
  return (
    <section className="panel table-panel strategy-table-panel">
      <div className="panel-header"><div><h2>策略股票列表</h2><span>所有来源统一为相同字段，重复命中会保留来源信息</span></div><ListChecks size={19} /></div>
      <div className="table-wrap">
        <table className="strategy-table">
          <thead><tr><th>股票</th><th>代码</th><th>市场</th><th>策略来源</th><th>命中策略</th><th>最新价</th><th>涨跌幅</th><th>入选时间</th></tr></thead>
          <tbody>
            {stocks.map(stock => {
              const change = stock.metrics?.最新涨跌幅 ?? stock.metrics?.涨跌幅;
              return (
                <tr key={`${stock.source_id}-${stock.strategy_id}-${stock.code}`}>
                  <td><strong>{stock.name || '-'}</strong></td><td>{stock.code}</td><td>{stock.market || '-'}</td><td>{stock.source_name}</td>
                  <td className="strategy-name-cell" title={stock.strategy_name}>{stock.strategy_name}</td>
                  <td>{formatValue(stock.metrics?.最新价 ?? stock.metrics?.收盘价)}</td><td className={trendClass(change)}>{formatValue(change)}</td><td>{shortTime(stock.selected_at)}</td>
                </tr>
              );
            })}
            {!stocks.length ? <tr><td colSpan="8" className="empty">当前来源暂无策略股票</td></tr> : null}
          </tbody>
        </table>
      </div>
    </section>
  );
}
