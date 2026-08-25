import { useEffect, useMemo, useRef } from 'react';
import { ClientSideRowModelModule, colorSchemeDark, themeQuartz } from 'ag-grid-community';
import { AgGridProvider, AgGridReact } from 'ag-grid-react';
import StockKlinePanel from './StockKlinePanel.jsx';
import { useStockKline } from '../hooks/useStockKline.js';
import styles from './RankingTable.module.css';

const modules = [ClientSideRowModelModule];

const themeDarkBlue = themeQuartz.withPart(colorSchemeDark).withParams({
  backgroundColor: '#09090b'
});

const KLINE_ROW_HEIGHT = 586;

function stockSymbol(stock) {
  return stock?.thscode || stock?.code || '';
}

function RankingKlineRow({ data }) {
  const stock = data.stock;
  const { data: klineData, loading, error, loadKline } = useStockKline();

  useEffect(() => {
    loadKline(stockSymbol(stock));
  }, [loadKline, stock]);

  return (
    <div className={styles.klineRow}>
      <StockKlinePanel stock={stock} data={klineData} loading={loading} error={error} enableMouseWheelZoom={false} />
    </div>
  );
}

function keepKlineRowsWithStocks({ nodes }) {
  const klineRowsByStock = new Map(
    nodes.filter(node => node.data?.rowType === 'kline').map(node => [node.data.parentRowId, node])
  );
  const stockRows = nodes.filter(node => node.data?.rowType !== 'kline');

  nodes.length = 0;
  stockRows.forEach(stockRow => {
    nodes.push(stockRow);
    const klineRow = klineRowsByStock.get(stockRow.data.rowId);
    if (klineRow) nodes.push(klineRow);
  });
}

export default function RankingTable({ rows, loading }) {
  const columnDefs = useRef([
    { headerName: '股票', field: 'name', flex: 1 },
    { headerName: '代码', field: 'thscode', flex: 1 },
    { headerName: '排名', field: 'rank', flex: 0.7, minWidth: 72 },
    { headerName: '热度', field: 'heat', flex: 1 }
  ]);

  // 构造K线图数据行
  const rowData = useMemo(
    () =>
      rows.flatMap((row, index) => {
        const rowKey = `${stockSymbol(row) || 'stock'}-${index}`;
        const stockRowId = `stock-${rowKey}`;
        return [
          {
            ...row,
            rowId: stockRowId
          },
          {
            rowType: 'kline',
            rowId: `kline-${rowKey}`,
            parentRowId: stockRowId,
            stock: row
          }
        ];
      }),
    [rows]
  );

  return (
    <>
      <div className={styles.grid}>
        <AgGridProvider modules={modules}>
          <div style={{ height: '100%', width: '100%' }}>
            <AgGridReact
              theme={themeDarkBlue}
              rowData={rowData}
              columnDefs={columnDefs.current}
              defaultColDef={{ resizable: true, sortable: true }}
              fullWidthCellRenderer={RankingKlineRow}
              getRowHeight={params => (params.data?.rowType === 'kline' ? KLINE_ROW_HEIGHT : undefined)}
              getRowId={params => params.data.rowId}
              isFullWidthRow={params => params.rowNode.data?.rowType === 'kline'}
              loading={loading}
              postSortRows={keepKlineRowsWithStocks}
            />
          </div>
        </AgGridProvider>
      </div>
    </>
  );
}
