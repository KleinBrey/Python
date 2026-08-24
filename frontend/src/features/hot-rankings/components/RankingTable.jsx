import { useMemo } from 'react';
import { ClientSideRowModelModule, colorSchemeDark, themeQuartz } from 'ag-grid-community';
import { AgGridProvider, AgGridReact } from 'ag-grid-react';

const modules = [ClientSideRowModelModule];

const themeDarkBlue = themeQuartz.withPart(colorSchemeDark).withParams({
  backgroundColor: '#09090b'
});

export default function RankingTable({ ranking, loading, onRowClick }) {
  const columnDefs = useMemo(
    () => [
      { headerName: '排名', field: 'rank', flex: 1 },
      { headerName: '股票', field: 'name', flex: 1 },
      { headerName: '代码', field: 'thscode', flex: 1 },
      { headerName: '热度', field: 'heat', flex: 1 }
    ],
    []
  );

  return (
    <>
      <div className="ag-grid-container">
        <AgGridProvider modules={modules}>
          <div style={{ height: '100%', width: '100%' }}>
            <AgGridReact
              theme={themeDarkBlue}
              rowData={ranking.rows}
              columnDefs={columnDefs}
              defaultColDef={{ resizable: true, sortable: true }}
              loading={loading}
              onRowClicked={event => onRowClick?.(event.data)}
            />
          </div>
        </AgGridProvider>
      </div>
    </>
  );
}
