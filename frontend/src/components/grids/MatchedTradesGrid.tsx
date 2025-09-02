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
  selectedMatchId?: string | null;
  onRowClick?: (matchId: string | null) => void;
}

const MatchedTradesGrid: React.FC<MatchedTradesGridProps> = ({ 
  refreshTrigger, 
  selectedMatchId, 
  onRowClick 
}) => {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [trades, setTrades] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const gridRef = useRef<AgGridReact>(null);

  // Get client ID from user context
  const clientId = user?.organization?.id || user?.id;

  // Helper function to create cell renderer with difference highlighting
  const createCellRenderer = (fieldName: string) => (params: any) => {
    const value = params.value || '';
    const differingFields = params.data?.differingFields || [];
    const hasDifference = differingFields.includes(fieldName);
    
    return React.createElement('div', {
      style: {
        backgroundColor: hasDifference ? '#ff0000' : 'transparent', // Red background for differences
        color: hasDifference ? '#ffffff' : 'inherit', // White text for differences
        padding: '2px 4px',
        width: '100%',
        height: '100%',
        display: 'flex',
        alignItems: 'center'
      }
    }, value);
  };

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
  
  // Refresh cell styles when selectedMatchId changes to update row highlighting
  useEffect(() => {
    if (gridRef.current?.api) {
      // Use redrawRows() instead of refreshCells() to trigger getRowStyle recalculation
      gridRef.current.api.redrawRows();
    }
  }, [selectedMatchId]);
  
  const columnDefs: ColDef[] = useMemo(() => [
    { 
      headerName: t('grid.columns.confidence'), 
      field: 'match_confidence', 
      width: 120, 
      sortable: true, 
      filter: true,
      cellRenderer: (params: any) => {
        // Handle both "100%" string and 100 number formats
        let confidenceNum;
        let displayValue;
        
        if (typeof params.value === 'string' && params.value.includes('%')) {
          // Already formatted as "100%" - extract number and use as-is
          confidenceNum = parseInt(params.value, 10);
          displayValue = params.value;
        } else {
          // Raw number - add % symbol
          confidenceNum = params.value || 0;
          displayValue = `${confidenceNum}%`;
        }
        
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
        }, displayValue);
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
      width: 120,
      cellRenderer: createCellRenderer('ProductType')
    },
    { 
      headerName: t('grid.columns.tradeDate'), 
      field: 'TradeDate', 
      width: 120,
      sortable: true, 
      filter: true,
      cellRenderer: (params: any) => {
        const value = params.value || '';
        const formattedValue = value ? (() => {
          const [day, month, year] = value.split('-');
          const date = new Date(year, month - 1, day);
          const dayName = date.toLocaleDateString('es-CL', { weekday: 'short' });
          return `${dayName} ${day}-${month}-${year}`;
        })() : '';
        
        const differingFields = params.data?.differingFields || [];
        const hasDifference = differingFields.includes('TradeDate');
        
        return React.createElement('div', {
          style: {
            backgroundColor: hasDifference ? '#ff0000' : 'transparent',
            color: hasDifference ? '#ffffff' : 'inherit',
            padding: '2px 4px',
            width: '100%',
            height: '100%',
            display: 'flex',
            alignItems: 'center'
          }
        }, formattedValue);
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
      width: 60,
      cellRenderer: createCellRenderer('Direction')
    },
    { 
      headerName: t('grid.columns.currency1'), 
      field: 'Currency1', 
      width: 100,
      cellRenderer: createCellRenderer('Currency1')
    },
    { 
      headerName: t('grid.columns.amount'), 
      field: 'QuantityCurrency1', 
      width: 140,
      cellRenderer: (params: any) => {
        const value = params.value || 0;
        const formattedValue = value.toLocaleString('en-US', {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2
        });
        
        const differingFields = params.data?.differingFields || [];
        const hasDifference = differingFields.includes('QuantityCurrency1');
        
        return React.createElement('div', {
          style: {
            backgroundColor: hasDifference ? '#ff0000' : 'transparent',
            color: hasDifference ? '#ffffff' : 'inherit',
            padding: '2px 4px',
            width: '100%',
            height: '100%',
            display: 'flex',
            alignItems: 'center'
          }
        }, formattedValue);
      }
    },
    { 
      headerName: t('grid.columns.price'), 
      field: 'Price', 
      width: 100,
      cellRenderer: (params: any) => {
        const value = params.value || 0;
        const formattedValue = value.toLocaleString('en-US', {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2
        });
        
        const differingFields = params.data?.differingFields || [];
        const hasDifference = differingFields.includes('Price');
        
        return React.createElement('div', {
          style: {
            backgroundColor: hasDifference ? '#ff0000' : 'transparent',
            color: hasDifference ? '#ffffff' : 'inherit',
            padding: '2px 4px',
            width: '100%',
            height: '100%',
            display: 'flex',
            alignItems: 'center'
          }
        }, formattedValue);
      }
    },
    { 
      headerName: t('grid.columns.currency2'), 
      field: 'Currency2', 
      width: 100,
      cellRenderer: createCellRenderer('Currency2')
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
      width: 140,
      cellRenderer: createCellRenderer('FixingReference')
    },
    { 
      headerName: t('grid.columns.settlementType'), 
      field: 'SettlementType', 
      width: 130,
      cellRenderer: createCellRenderer('SettlementType')
    },
    { 
      headerName: t('grid.columns.settlementCurrency'), 
      field: 'SettlementCurrency', 
      width: 140,
      cellRenderer: createCellRenderer('SettlementCurrency')
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
      width: 200,
      cellRenderer: createCellRenderer('CounterpartyPaymentMethod')
    },
    { 
      headerName: t('grid.columns.ourPaymentMethod'), 
      field: 'OurPaymentMethod', 
      width: 160,
      cellRenderer: createCellRenderer('OurPaymentMethod')
    }
  ], [t]);

  // Handle row click for highlighting
  const handleRowClick = useCallback((event: any) => {
    // Check both possible field names for match_id
    const matchId = event.data?.match_id || event.data?.matchId || null;
    
    if (onRowClick) {
      onRowClick(matchId);
    }
  }, [onRowClick]);

  // Row styling for highlighting
  const getRowStyle = useCallback((params: any) => {
    // Check both possible field names for match_id
    const matchId = params.data?.match_id || params.data?.matchId;
    
    if (selectedMatchId && matchId && matchId === selectedMatchId) {
      return { backgroundColor: '#264a73' }; // Highlight color for selected row
    }
    return undefined;
  }, [selectedMatchId]);

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
            onRowClicked={handleRowClick}
            getRowStyle={getRowStyle}
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