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

// Using v1.0 field structure directly

const ClientTradesGrid: React.FC = () => {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [trades, setTrades] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Get client ID from user context (assuming user has organization data)
  const clientId = user?.organization?.id || user?.id;

  useEffect(() => {
    if (!clientId) {
      setLoading(false);
      setError('No client ID available');
      return;
    }

    const loadTrades = async () => {
      try {
        setLoading(true);
        setError(null);
        const tradesData = await clientService.getUnmatchedTrades(clientId);
        setTrades(tradesData);
      } catch (error) {
        console.error('Error loading trades:', error);
        setError(error instanceof Error ? error.message : 'Failed to load trades');
      } finally {
        setLoading(false);
      }
    };

    loadTrades();
  }, [clientId]);
  
  const columnDefs: ColDef[] = useMemo(() => [
    { 
      headerName: t('grid.columns.tradeNumber'), 
      field: 'TradeNumber', 
      width: 70, 
      sortable: true, 
      filter: true 
    },
    { 
      headerName: t('grid.columns.counterparty'), 
      field: 'CounterpartyName', 
      width: 180, 
      sortable: true, 
      filter: true 
    },
    { 
      headerName: t('grid.columns.productType'), 
      field: 'ProductType', 
      width: 120, 
      sortable: true, 
      filter: true 
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
      width: 60, 
      sortable: true, 
      filter: true 
    },
    { 
      headerName: t('grid.columns.currency1'), 
      field: 'Currency1', 
      width: 90, 
      sortable: true, 
      filter: true 
    },
    { 
      headerName: t('grid.columns.amount'), 
      field: 'QuantityCurrency1', 
      width: 100, 
      sortable: true, 
      filter: true, 
      valueFormatter: (params) => params.value.toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }) 
    },
    { 
      headerName: t('grid.columns.price'), 
      field: 'ForwardPrice', 
      width: 110, 
      sortable: true, 
      filter: true, 
      valueFormatter: (params) => params.value.toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }) 
    },
    { 
      headerName: t('grid.columns.currency2'), 
      field: 'Currency2', 
      width: 90, 
      sortable: true, 
      filter: true 
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
        const dayName = date.toLocaleDateString('en-US', { weekday: 'short' });
        return `${dayName} ${day}-${month}-${year}`;
      }
    },
    { 
      headerName: t('grid.columns.fixingReference'), 
      field: 'FixingReference', 
      width: 100, 
      sortable: true, 
      filter: true 
    },
    { 
      headerName: t('grid.columns.settlementType'), 
      field: 'SettlementType', 
      width: 100, 
      sortable: true, 
      filter: true 
    },
    { 
      headerName: t('grid.columns.settlementCurrency'), 
      field: 'SettlementCurrency', 
      width: 100, 
      sortable: true, 
      filter: true 
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
        const dayName = date.toLocaleDateString('en-US', { weekday: 'short' });
        return `${dayName} ${day}-${month}-${year}`;
      }
    },
    { 
      headerName: t('grid.columns.counterpartyPaymentMethod'), 
      field: 'CounterpartyPaymentMethod', 
      width: 100, 
      sortable: true, 
      filter: true 
    },
    { 
      headerName: t('grid.columns.ourPaymentMethod'), 
      field: 'OurPaymentMethod', 
      width: 100, 
      sortable: true, 
      filter: true 
    }
  ], [t]);

  const getContextMenuItems = useCallback((params: GetContextMenuItemsParams): (string | MenuItemDef)[] => [
    {
      name: t('grid.contextMenu.viewDetails'),
      action: () => {/* View details action */}
    },
    {
      name: t('grid.contextMenu.edit'),
      action: () => {/* Edit trade action */}
    },
    {
      name: t('grid.contextMenu.delete'),
      action: () => {/* Delete trade action */}
    },
    'separator',
    {
      name: t('grid.contextMenu.duplicate'),
      action: () => {/* Duplicate trade action */}
    }
  ], [t]);

  if (loading) {
    return (
      <div className="ag-theme-alpine-dark trade-grid loading-state">
        <div className="loading-message">Loading trades...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="ag-theme-alpine-dark trade-grid error-state">
        <div className="error-message">
          Error loading trades: {error}
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
          No unmatched trades found. Upload a trade file to get started.
        </div>
      ) : (
        <AgGridReact
          rowData={trades}
          columnDefs={columnDefs}
          getContextMenuItems={getContextMenuItems}
          pagination={true}
          paginationPageSize={100}
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

export default ClientTradesGrid;