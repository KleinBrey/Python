import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/shadcn/components/ui/table.jsx';
import { formatValue } from '@/utils/formatters.js';

export default function StockSelectionTable({ rows, selectedStock, onSelect }) {
  return (
    <aside className="iwencai-stock-selector">
      <div className="iwencai-stock-selector-head"><strong>股票列表</strong><span>{rows.length} 只</span></div>
      <Table containerClassName="iwencai-stock-table-scroll" style={{ minWidth: 374 }}>
        <TableHeader><TableRow><TableHead style={{ width: 112 }}>代码</TableHead><TableHead style={{ width: 108 }}>股票</TableHead><TableHead style={{ width: 76 }}>最新价</TableHead><TableHead style={{ width: 78 }}>涨跌幅</TableHead></TableRow></TableHeader>
        <TableBody>{rows.map((row, index) => {
          const selected = row.股票代码 === selectedStock?.股票代码;
          return (
            <TableRow aria-selected={selected} data-state={selected ? 'selected' : undefined} key={`${row.股票代码 || 'stock'}-${index}`} onClick={() => onSelect(row)} onKeyDown={event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); onSelect(row); } }} role="button" tabIndex={0}>
              <TableCell title={String(row.股票代码 || '')}>{formatValue(row.股票代码)}</TableCell><TableCell title={String(row.股票简称 || '')}>{formatValue(row.股票简称)}</TableCell><TableCell>{formatValue(row.最新价)}</TableCell><TableCell>{formatValue(row.最新涨跌幅)}</TableCell>
            </TableRow>
          );
        })}</TableBody>
      </Table>
    </aside>
  );
}
