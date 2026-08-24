import { useMemo } from 'react';
import { AllCommunityModule, colorSchemeDark, themeQuartz } from 'ag-grid-community';
import { AgGridProvider, AgGridReact } from 'ag-grid-react';
import { Loader2, RefreshCcw } from 'lucide-react';
import moment from 'moment';

import { Button } from '@/components/ui/button.jsx';

const modules = [AllCommunityModule];

const themeDarkBlue = themeQuartz.withPart(colorSchemeDark).withParams({
  backgroundColor: '#09090b'
});

function formatTimestamp(timestamp) {
  if (!timestamp) return '未刷新';

  const value = moment(timestamp);
  return value.isValid() ? value.format('YYYY-MM-DD HH:mm:ss') : '未刷新';
}

export default function RankingTable({ ranking, loading, error, onRefresh, onRowClick }) {
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
      <div className="panel-header" style={{ gridColumn: '1 / -1' }}>
        <div>
          <h2>{ranking.title}</h2>
          <span>{error || formatTimestamp(ranking.timestamp)}</span>
        </div>
        <Button
          type="button"
          className="ghost-button"
          variant="outline"
          onClick={onRefresh}
          disabled={loading}
        >
          {loading ? <Loader2 className="spin" size={15} /> : <RefreshCcw size={15} />}
          <span>{loading ? '更新中' : '刷新当前'}</span>
        </Button>
      </div>

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
