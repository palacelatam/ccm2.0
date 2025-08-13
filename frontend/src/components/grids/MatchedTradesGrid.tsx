import React, { useCallback, useMemo, useState, useEffect, useRef } from 'react';
import { AgGridReact } from 'ag-grid-react';
import { ColDef, GetContextMenuItemsParams, MenuItemDef } from 'ag-grid-community';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../auth/AuthContext';
import { clientService, ClientService } from '../../services/clientService';
import StatusCellRenderer from './StatusCellRenderer';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';
import './TradeGrid.css';

interface MatchedTradesGridProps {
  refreshTrigger?: number;
}

const MatchedTradesGrid: React.FC<MatchedTradesGridProps> = ({ refreshTrigger }) => {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [trades, setTrades] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const gridRef = useRef<AgGridReact>(null);

  // Get client ID from user context
  const clientId = user?.organization?.id || user?.id;

  const loadMatchedTrades = useCallback(async (preserveGridState = false) => {
    if (!clientId) {
      setLoading(false);
      setError('No client ID available');
      return;
    }

    try {
      if (!preserveGridState) {
        setLoading(true);
      }
      setError(null);
      const tradesData = await clientService.getMatchedTrades(clientId);
      
      if (preserveGridState && gridRef.current?.api) {
        // Update data while preserving grid state (sorting, filtering, etc.)
        gridRef.current.api.setRowData(tradesData);
      } else {
        // Full reload (initial load)
        setTrades(tradesData);
      }
    } catch (error) {
      console.error('Error loading matched trades:', error);
      setError(error instanceof Error ? error.message : 'Failed to load matched trades');
    } finally {
      if (!preserveGridState) {
        setLoading(false);
      }
    }
  }, [clientId]);

  // Load trades on mount and when client changes
  useEffect(() => {
    loadMatchedTrades();
  }, [loadMatchedTrades]);

  // Refresh when refreshTrigger changes (called by parent)
  useEffect(() => {
    if (refreshTrigger && refreshTrigger > 0) {
      loadMatchedTrades(true); // Preserve grid state on refresh
    }
  }, [refreshTrigger, loadMatchedTrades]);
  
  const columnDefs: ColDef[] = useMemo(() => [
    { 
      headerName: t('grid.columns.confidence'), 
      field: 'match_confidence', 
      width: 120, 
      sortable: true, 
      filter: true,
      cellRenderer: (params: any) => {
        // Extract numeric value from string like "92%"
        const confidenceStr = params.value || "0%";
        const confidenceNum = parseInt(confidenceStr, 10);
        
        let color;
        if (confidenceNum >= 90) {
          color = '#4CAF50'; // Green
        } else if (confidenceNum >= 70) {
          color = '#FB9205'; // Orange
        } else {
          color = '#ff4444'; // Red
        }
        
        return React.createElement('div', { 
          style: { color: color, fontWeight: 'bold' } 
        }, confidenceStr);
      }
    },
    { 
      headerName: t('grid.columns.tradeNumber'), 
      field: 'TradeNumber', 
      width: 70 
    },
    { 
      headerName: t('grid.columns.counterparty'), 
      field: 'CounterpartyName', 
      width: 150 
    },
    { 
      headerName: t('grid.columns.productType'), 
      field: 'ProductType', 
      width: 120 
    },
    { 
      headerName: t('grid.columns.tradeDate'), 
      field: 'TradeDate', 
      width: 120,
      sortable: true, 
      filter: true,
      valueFormatter: (params) => {
        if (!params.value) return '';
        const [day, month, year] = params.value.split('-');
        const date = new Date(year, month - 1, day);
        const dayName = date.toLocaleDateString('es-CL', { weekday: 'short' });
        return `${dayName} ${day}-${month}-${year}`;
      }
    },
    { 
      headerName: t('grid.columns.valueDate'), 
      field: 'ValueDate', 
      width: 120,
      sortable: true, 
      filter: true,
      valueFormatter: (params) => {
        if (!params.value) return '';
        const [day, month, year] = params.value.split('-');
        const date = new Date(year, month - 1, day);
        const dayName = date.toLocaleDateString('es-CL', { weekday: 'short' });
        return `${dayName} ${day}-${month}-${year}`;
      }
    },
    { 
      headerName: t('grid.columns.direction'), 
      field: 'Direction', 
      width: 60 
    },
    { 
      headerName: t('grid.columns.currency1'), 
      field: 'Currency1', 
      width: 100 
    },
    { 
      headerName: t('grid.columns.amount'), 
      field: 'QuantityCurrency1', 
      width: 140,
      valueFormatter: (params) => params.value.toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })
    },
    { 
      headerName: t('grid.columns.price'), 
      field: 'ForwardPrice', 
      width: 100,
      valueFormatter: (params) => params.value.toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })
    },
    { 
      headerName: t('grid.columns.currency2'), 
      field: 'Currency2', 
      width: 100 
    },
    { 
      headerName: t('grid.columns.maturityDate'), 
      field: 'MaturityDate', 
      width: 120,
      sortable: true, 
      filter: true,
      valueFormatter: (params) => {
        if (!params.value) return '';
        const [day, month, year] = params.value.split('-');
        const date = new Date(year, month - 1, day);
        const dayName = date.toLocaleDateString('es-CL', { weekday: 'short' });
        return `${dayName} ${day}-${month}-${year}`;
      }
    },
    { 
      headerName: t('grid.columns.fixingReference'), 
      field: 'FixingReference', 
      width: 140 
    },
    { 
      headerName: t('grid.columns.settlementType'), 
      field: 'SettlementType', 
      width: 130 
    },
    { 
      headerName: t('grid.columns.settlementCurrency'), 
      field: 'SettlementCurrency', 
      width: 140 
    },
    { 
      headerName: t('grid.columns.paymentDate'), 
      field: 'PaymentDate', 
      width: 120,
      sortable: true, 
      filter: true,
      valueFormatter: (params) => {
        if (!params.value) return '';
        const [day, month, year] = params.value.split('-');
        const date = new Date(year, month - 1, day);
        const dayName = date.toLocaleDateString('es-CL', { weekday: 'short' });
        return `${dayName} ${day}-${month}-${year}`;
      }
    },
    { 
      headerName: t('grid.columns.counterpartyPaymentMethod'), 
      field: 'CounterpartyPaymentMethod', 
      width: 200 
    },
    { 
      headerName: t('grid.columns.ourPaymentMethod'), 
      field: 'OurPaymentMethod', 
      width: 160 
    }
  ], [t]);

  const getContextMenuItems = useCallback((params: GetContextMenuItemsParams): (string | MenuItemDef)[] => [
    {
      name: t('grid.contextMenu.viewTradeDetails'),
      action: () => {/* View trade details action */}
    },
    {
      name: t('grid.contextMenu.viewEmailDetails'),
      action: () => {/* View email details action */}
    },
    {
      name: t('grid.contextMenu.reviewMatch'),
      action: () => {/* Review match action */}
    },
    'separator',
    {
      name: t('grid.contextMenu.confirmMatch'),
      action: () => {/* Confirm match action */}
    },
    {
      name: t('grid.contextMenu.disputeMatch'),
      action: () => {/* Dispute match action */}
    }
  ], [t]);

  if (loading) {
    return (
      <div className="ag-theme-alpine-dark trade-grid loading-state">
        <div className="loading-message">Loading matched trades...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="ag-theme-alpine-dark trade-grid error-state">
        <div className="error-message">
          Error loading matched trades: {error}
          <button 
            onClick={() => window.location.reload()} 
            className="retry-button"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ height: '100%', width: '100%', display: 'flex', flexDirection: 'column', minHeight: 0 }}>
      {trades.length === 0 ? (
        <div className="empty-state" style={{ flex: '1', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#b3b3b3' }}>
          No matched trades found. Process matches to see matched trades here.
        </div>
      ) : (
        <div className="ag-theme-alpine-dark trade-grid" style={{ flex: '1', minHeight: 0, height: '100%' }}>
          <AgGridReact
            ref={gridRef}
            rowData={trades}
            columnDefs={columnDefs}
            getContextMenuItems={getContextMenuItems}
            pagination={true}
            paginationPageSize={50}
            enableRangeSelection={true}
            allowContextMenuWithControlKey={true}
            suppressMovableColumns={false}
            defaultColDef={{
              sortable: true,
              filter: true,
              resizable: true,
              minWidth: 80
            }}
          />
        </div>
      )}
    </div>
  );
};

export default MatchedTradesGrid;