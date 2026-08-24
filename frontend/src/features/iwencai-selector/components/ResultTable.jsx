import { useEffect, useMemo, useState } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

import { Button } from '@/components/ui/button.jsx';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table.jsx';
import { formatValue } from '@/utils/formatters.js';
import { collectColumns } from '../utils/tableColumns.js';

export default function ResultTable({ rows }) {
  const keys = useMemo(() => collectColumns(rows), [rows]);
  const [pageSize, setPageSize] = useState(50);
  const [page, setPage] = useState(1);
  const pageCount = Math.max(1, Math.ceil(rows.length / pageSize));
  const currentPage = Math.min(page, pageCount);
  const visibleRows = rows.slice((currentPage - 1) * pageSize, currentPage * pageSize);

  useEffect(() => setPage(1), [rows.length, pageSize]);

  return (
    <div className="iwencai-result-table">
      <Table containerClassName="iwencai-result-table-scroll" style={{ minWidth: Math.max(960, keys.length * 150) }}>
        <TableHeader><TableRow>{keys.map(key => <TableHead className={key === '股票代码' ? 'sticky-code-column' : ''} key={key} style={{ width: key.includes('名称') || key.includes('简称') ? 140 : 150 }}>{key}</TableHead>)}</TableRow></TableHeader>
        <TableBody>
          {visibleRows.length ? visibleRows.map((row, rowIndex) => (
            <TableRow key={`${row.股票代码 || 'stock'}-${(currentPage - 1) * pageSize + rowIndex}`}>
              {keys.map(key => <TableCell className={key === '股票代码' ? 'sticky-code-column' : ''} key={key}><span title={row[key] == null ? '' : String(row[key])}>{formatValue(row[key])}</span></TableCell>)}
            </TableRow>
          )) : <TableRow><TableCell className="table-empty-state" colSpan={Math.max(1, keys.length)}>没有查询到股票，请尝试简化或放宽条件</TableCell></TableRow>}
        </TableBody>
      </Table>
      <div className="table-pagination">
        <span>第 {currentPage} / {pageCount} 页，共 {rows.length} 条</span>
        <div className="table-pagination-actions">
          <label>每页<select aria-label="每页显示数量" className="shadcn-select" onChange={event => setPageSize(Number(event.target.value))} value={pageSize}>{[20, 50, 100].map(size => <option key={size} value={size}>{size}</option>)}</select></label>
          <Button disabled={currentPage <= 1} onClick={() => setPage(value => Math.max(1, value - 1))} size="sm" type="button" variant="outline"><ChevronLeft size={14} />上一页</Button>
          <Button disabled={currentPage >= pageCount} onClick={() => setPage(value => Math.min(pageCount, value + 1))} size="sm" type="button" variant="outline">下一页<ChevronRight size={14} /></Button>
        </div>
      </div>
    </div>
  );
}
