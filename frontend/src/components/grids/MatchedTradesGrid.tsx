import React, { useCallback, useMemo, useState, useEffect } from 'react';
import { AgGridReact } from 'ag-grid-react';
import { ColDef, GetContextMenuItemsParams, MenuItemDef } from 'ag-grid-community';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../auth/AuthContext';
import { clientService, ClientService } from '../../services/clientService';
import StatusCellRenderer from './StatusCellRenderer';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';
import './TradeGrid.css';

const MatchedTradesGrid: React.FC = () => {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [trades, setTrades] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Get client ID from user context
  const clientId = user?.organization?.id || user?.id;

  useEffect(() => {
    if (!clientId) {
      setLoading(false);
      setError('No client ID available');
      return;
    }

    const loadMatchedTrades = async () => {
      try {
        setLoading(true);
        setError(null);
        const tradesData = await clientService.getMatchedTrades(clientId);
        setTrades(tradesData);
      } catch (error) {
        console.error('Error loading matched trades:', error);
        setError(error instanceof Error ? error.message : 'Failed to load matched trades');
      } finally {
        setLoading(false);
      }
    };

    loadMatchedTrades();
  }, [clientId]);
  
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
    <div className="ag-theme-alpine-dark trade-grid">
      {trades.length === 0 ? (
        <div className="empty-state">
          No matched trades found. Process matches to see matched trades here.
        </div>
      ) : (
        <AgGridReact
          rowData={trades}
          columnDefs={columnDefs}
          getContextMenuItems={getContextMenuItems}
          pagination={true}
          paginationPageSize={50}
          enableRangeSelection={true}
          allowContextMenuWithControlKey={true}
          suppressMovableColumns={false}
          domLayout="autoHeight"
          defaultColDef={{
            sortable: true,
            filter: true,
            resizable: true,
            minWidth: 80
          }}
        />
      )}
    </div>
  );
};

export default MatchedTradesGrid;