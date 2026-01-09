import React, { useRef, useEffect, useMemo, useCallback } from 'react';
import { AgGridReact } from 'ag-grid-react';
import { ColDef } from 'ag-grid-community';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';
import { useSharedWorker } from '@/shared/lib/useSharedWorker';

function LiveTickerGrid() {
  const gridRef = useRef<AgGridReact>(null);
  const dataBuffer = useRef<any[]>([]);

  const handleWorkerMessage = useCallback((message: any) => {
    try {
      const data = JSON.parse(message.payload);
      if (data.type === 'HEARTBEAT') {
        const mockTick = {
          symbol: 'SYSTEM_PULSE',
          lastPrice: new Date(data.timestamp).getSeconds(),
          timestamp: data.timestamp,
        };
        dataBuffer.current.push(mockTick);
      }
    } catch (e) { /* Ignore */ }
  }, []);

  useSharedWorker(handleWorkerMessage);

  useEffect(() => {
    let animationFrameId: number;
    const updateGrid = () => {
      // Only proceed if the grid API is ready
      if (dataBuffer.current.length > 0 && gridRef.current?.api) {
        const toAdd: any[] = [];
        const toUpdate: any[] = [];

        // Process the buffer
        dataBuffer.current.forEach(tick => {
          // Direct API check: Does this row exist?
          const rowNode = gridRef.current!.api.getRowNode(tick.symbol);
          if (rowNode) {
            toUpdate.push(tick);
          } else {
            toAdd.push(tick);
          }
        });

        // Clear buffer immediately to prevent double processing
        dataBuffer.current = [];

        // Apply transaction
        gridRef.current.api.applyTransactionAsync({
          add: toAdd,
          update: toUpdate,
        });
      }
      animationFrameId = requestAnimationFrame(updateGrid);
    };
    animationFrameId = requestAnimationFrame(updateGrid);
    return () => cancelAnimationFrame(animationFrameId);
  }, []);

  const columnDefs: ColDef[] = useMemo(() => [
    { field: 'symbol', headerName: 'Symbol', width: 150, suppressMovable: true },
    { 
      field: 'lastPrice', 
      headerName: 'Price', 
      width: 120, 
      cellStyle: { fontFamily: 'IBM Plex Mono' },
      valueFormatter: params => params.value ? params.value.toFixed(2) : '0.00'
    },
    { 
      field: 'timestamp', 
      headerName: 'Timestamp', 
      flex: 1,
      valueFormatter: params => params.value ? new Date(params.value).toLocaleTimeString() : ''
    },
  ], []);

  const getRowId = useMemo(() => (params: any) => params.data.symbol, []);

  return (
    <div className="ag-theme-alpine-dark h-full w-full">
      <AgGridReact
        ref={gridRef}
        columnDefs={columnDefs}
        getRowId={getRowId}
        rowData={[]}
        animateRows={true}
      />
    </div>
  );
};

export default LiveTickerGrid;
