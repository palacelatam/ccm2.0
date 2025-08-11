import React, { useCallback, useMemo, useState, useEffect } from 'react';
import { AgGridReact } from 'ag-grid-react';
import { ColDef, GetContextMenuItemsParams, MenuItemDef } from 'ag-grid-community';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../auth/AuthContext';
import { clientService, EmailConfirmation, ClientService } from '../../services/clientService';
import StatusCellRenderer from './StatusCellRenderer';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';
import './TradeGrid.css';

// Using v1.0 field structure for email confirmations with extracted trade data

const ConfirmationsGrid: React.FC = () => {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [emails, setEmails] = useState<EmailConfirmation[]>([]);
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

    const loadEmails = async () => {
      try {
        setLoading(true);
        setError(null);
        const emailsData = await clientService.getAllEmailConfirmations(clientId);
        setEmails(emailsData);
      } catch (error) {
        console.error('Error loading email confirmations:', error);
        setError(error instanceof Error ? error.message : 'Failed to load email confirmations');
      } finally {
        setLoading(false);
      }
    };

    loadEmails();
  }, [clientId]);
  
  const columnDefs: ColDef[] = useMemo(() => [
    { 
      headerName: t('grid.columns.bankTradeNumber'), 
      field: 'BankTradeNumber', 
      width: 80 
    },
    {
      headerName: t('grid.columns.status'),
      field: 'status',
      width: 110,
      sortable: true,
      filter: true,
      cellRenderer: (params: any) => {
        const status = params.value;
        let color = '#FFFFFF';
        
        switch(status) {
          case 'Confirmation OK':
            color = '#4CAF50';
            break;
          case 'Difference':
            color = '#ff4444';
            break;
          case 'Unrecognized':
            color = '#FFFFFF';
            break;
          case 'Resolved':
            color = '#00e7ff';
            break;
          case 'Tagged':
            color = '#FB9205';
            break;
        }
        
        return React.createElement('div', { 
          style: { color: color, fontWeight: 'bold' } 
        }, status);
      }
    },
    { 
      headerName: t('grid.columns.sender'), 
      field: 'EmailSender', 
      width: 150 
    },
    { 
      headerName: t('grid.columns.received'), 
      field: 'EmailDate', 
      width: 120 
    },
    { 
      headerName: t('grid.columns.time'), 
      field: 'EmailTime', 
      width: 120 
    },
    { 
      headerName: t('grid.columns.subject'), 
      field: 'EmailSubject', 
      width: 200 
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
      width: 100
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
      width: 120,
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
      name: t('grid.contextMenu.viewOriginalEmail'),
      action: () => {/* View email action */}
    },
    {
      name: t('grid.contextMenu.markProcessed'),
      action: () => {/* Mark processed action */}
    },
    {
      name: t('grid.contextMenu.reject'),
      action: () => {/* Reject action */}
    },
    'separator',
    {
      name: t('grid.contextMenu.viewDetails'),
      action: () => {/* View details action */}
    }
  ], [t]);

  if (loading) {
    return (
      <div className="ag-theme-alpine-dark trade-grid loading-state">
        <div className="loading-message">Loading email confirmations...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="ag-theme-alpine-dark trade-grid error-state">
        <div className="error-message">
          Error loading emails: {error}
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
      {emails.length === 0 ? (
        <div className="empty-state">
          No email confirmations found. Upload email files to get started.
        </div>
      ) : (
        <AgGridReact
          rowData={emails}
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

export default ConfirmationsGrid;