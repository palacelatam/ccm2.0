import React, { useCallback, useMemo } from 'react';
import { AgGridReact } from 'ag-grid-react';
import { ColDef, GetContextMenuItemsParams, MenuItemDef } from 'ag-grid-community';
import { useTranslation } from 'react-i18next';
import StatusCellRenderer from './StatusCellRenderer';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';
import './TradeGrid.css';

interface Confirmation {
  tradeId: string;
  counterparty: string;
  productType: string;
  tradeDate: string;
  valueDate: string;
  direction: 'BUY' | 'SELL';
  currency1: string;
  currency2: string;
  amount: number;
  price: number;
  maturityDate?: string;
  fixingReference?: string;
  settlementType: string;
  settlementCurrency: string;
  paymentDate: string;
  ourPaymentMethod: string;
  counterpartyPaymentMethod: string;
  received: string;
  bank: string;
  status: 'PROCESSED' | 'PENDING' | 'UNRECOGNISED' | 'ERROR';
}

const mockConfirmations: Confirmation[] = [
  {
    tradeId: 'CONF001',
    counterparty: 'Banco Santander',
    productType: 'FX SPOT',
    tradeDate: '2024-01-15',
    valueDate: '2024-01-17',
    direction: 'BUY',
    currency1: 'USD',
    currency2: 'CLP',
    amount: 1000000,
    price: 890.52,
    maturityDate: '2024-01-17',
    fixingReference: 'SPOT',
    settlementType: 'DVP',
    settlementCurrency: 'CLP',
    paymentDate: '2024-01-17',
    ourPaymentMethod: 'SWIFT',
    counterpartyPaymentMethod: 'ACH',
    received: '2024-01-15T10:45:00',
    bank: 'Banco Santander',
    status: 'PROCESSED'
  },
  {
    tradeId: 'CONF002',
    counterparty: 'Banco de Chile',
    productType: 'FX FORWARD',
    tradeDate: '2024-01-15',
    valueDate: '2024-02-15',
    direction: 'SELL',
    currency1: 'EUR',
    currency2: 'CLP',
    amount: 500000,
    price: 948.35,
    maturityDate: '2024-02-15',
    fixingReference: 'EURS/CLP-BCCH',
    settlementType: 'NET',
    settlementCurrency: 'EUR',
    paymentDate: '2024-02-15',
    ourPaymentMethod: 'WIRE',
    counterpartyPaymentMethod: 'SWIFT',
    received: '2024-01-15T14:22:00',
    bank: 'Banco de Chile',
    status: 'PROCESSED'
  },
  {
    tradeId: 'CONF003',
    counterparty: 'Banco Estado',
    productType: 'FX NDF',
    tradeDate: '2024-01-16',
    valueDate: '2024-03-16',
    direction: 'SELL',
    currency1: 'BRL',
    currency2: 'USD',
    amount: 2000000,
    price: 5.1250,
    maturityDate: '2024-03-16',
    fixingReference: 'BRL/USD-PTAX',
    settlementType: 'CASH',
    settlementCurrency: 'USD',
    paymentDate: '2024-03-18',
    ourPaymentMethod: 'WIRE',
    counterpartyPaymentMethod: 'ACH',
    received: '2024-01-16T09:15:00',
    bank: 'Banco Estado',
    status: 'UNRECOGNISED'
  }
];

const ConfirmationsGrid: React.FC = () => {
  const { t } = useTranslation();
  
  const columnDefs: ColDef[] = useMemo(() => [
    { 
      field: 'received', 
      headerName: t('grid.columns.received'), 
      width: 140, 
      sortable: true,
      filter: 'agDateColumnFilter',
      resizable: true,
      valueFormatter: (params) => new Date(params.value).toLocaleString('es-CL')
    },
    { 
      field: 'bank', 
      headerName: t('grid.columns.bank'), 
      width: 120, 
      sortable: true,
      filter: 'agTextColumnFilter',
      resizable: true
    },
    { 
      field: 'tradeId', 
      headerName: t('grid.columns.tradeId'), 
      width: 120, 
      sortable: true,
      filter: 'agTextColumnFilter',
      resizable: true
    },
    { 
      field: 'productType', 
      headerName: t('grid.columns.productType'), 
      width: 120,
      sortable: true,
      filter: 'agTextColumnFilter',
      resizable: true
    },
    { 
      field: 'currency1', 
      headerName: t('grid.columns.currency1'), 
      width: 100,
      sortable: true,
      filter: 'agTextColumnFilter',
      resizable: true
    },
    { 
      field: 'currency2', 
      headerName: t('grid.columns.currency2'), 
      width: 100,
      sortable: true,
      filter: 'agTextColumnFilter',
      resizable: true
    },
    { 
      field: 'amount', 
      headerName: t('grid.columns.amount'), 
      width: 120, 
      type: 'numericColumn',
      sortable: true,
      filter: 'agNumberColumnFilter',
      resizable: true,
      valueFormatter: (params) => new Intl.NumberFormat('es-CL').format(params.value)
    },
    { 
      field: 'price', 
      headerName: t('grid.columns.price'), 
      width: 120, 
      type: 'numericColumn',
      sortable: true,
      filter: 'agNumberColumnFilter',
      resizable: true,
      valueFormatter: (params) => params.value.toFixed(4)
    },
    { 
      field: 'status', 
      headerName: t('grid.columns.status'), 
      width: 120, 
      cellRenderer: StatusCellRenderer,
      sortable: true,
      filter: 'agTextColumnFilter',
      resizable: true
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

  return (
    <div className="ag-theme-alpine-dark trade-grid">
      <AgGridReact
        rowData={mockConfirmations}
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
    </div>
  );
};

export default ConfirmationsGrid;