import React, { useCallback, useMemo } from 'react';
import { AgGridReact } from 'ag-grid-react';
import { ColDef, GetContextMenuItemsParams, MenuItemDef } from 'ag-grid-community';
import { useTranslation } from 'react-i18next';
import StatusCellRenderer from './StatusCellRenderer';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';
import './TradeGrid.css';

interface MatchedTrade {
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
  status: 'MATCHED' | 'DISPUTED' | 'PENDING';
  confidence: number;
}

const mockMatchedTrades: MatchedTrade[] = [
  {
    tradeId: 'MT001',
    counterparty: 'Banco Santander',
    productType: 'FX SPOT',
    tradeDate: '2024-01-15',
    valueDate: '2024-01-17',
    direction: 'BUY',
    currency1: 'USD',
    currency2: 'CLP',
    amount: 1000000,
    price: 890.50,
    maturityDate: '2024-01-17',
    fixingReference: 'SPOT',
    settlementType: 'DVP',
    settlementCurrency: 'CLP',
    paymentDate: '2024-01-17',
    ourPaymentMethod: 'SWIFT',
    counterpartyPaymentMethod: 'ACH',
    status: 'MATCHED',
    confidence: 0.98
  },
  {
    tradeId: 'MT002',
    counterparty: 'Banco de Chile',
    productType: 'FX FORWARD',
    tradeDate: '2024-01-15',
    valueDate: '2024-02-15',
    direction: 'SELL',
    currency1: 'EUR',
    currency2: 'CLP',
    amount: 500000,
    price: 950.25,
    maturityDate: '2024-02-15',
    fixingReference: 'EURS/CLP-BCCH',
    settlementType: 'NET',
    settlementCurrency: 'EUR',
    paymentDate: '2024-02-15',
    ourPaymentMethod: 'WIRE',
    counterpartyPaymentMethod: 'SWIFT',
    status: 'DISPUTED',
    confidence: 0.87
  },
  {
    tradeId: 'MT003',
    counterparty: 'BCI',
    productType: 'FX SWAP',
    tradeDate: '2024-01-16',
    valueDate: '2024-01-18',
    direction: 'BUY',
    currency1: 'USD',
    currency2: 'CLP',
    amount: 750000,
    price: 891.75,
    maturityDate: '2024-04-18',
    fixingReference: 'USD/CLP-BCCH',
    settlementType: 'DVP',
    settlementCurrency: 'USD',
    paymentDate: '2024-01-18',
    ourPaymentMethod: 'ACH',
    counterpartyPaymentMethod: 'WIRE',
    status: 'PENDING',
    confidence: 0.92
  }
];

const MatchedTradesGrid: React.FC = () => {
  const { t } = useTranslation();
  
  const columnDefs: ColDef[] = useMemo(() => [
    { 
      field: 'tradeId', 
      headerName: t('grid.columns.tradeId'), 
      width: 120, 
      sortable: true,
      filter: 'agTextColumnFilter',
      resizable: true
    },
    { 
      field: 'counterparty', 
      headerName: t('grid.columns.counterparty'), 
      width: 150,
      sortable: true,
      filter: 'agTextColumnFilter',
      resizable: true
    },
    { 
      field: 'productType', 
      headerName: t('grid.columns.productType'), 
      width: 120, 
      filter: 'agTextColumnFilter',
      sortable: true,
      resizable: true
    },
    { 
      field: 'tradeDate', 
      headerName: t('grid.columns.tradeDate'), 
      width: 120, 
      sortable: true,
      filter: 'agDateColumnFilter',
      resizable: true
    },
    { 
      field: 'valueDate', 
      headerName: t('grid.columns.valueDate'), 
      width: 120, 
      sortable: true,
      filter: 'agDateColumnFilter',
      resizable: true
    },
    { 
      field: 'direction', 
      headerName: t('grid.columns.direction'), 
      width: 100,
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
      valueFormatter: (params) => new Intl.NumberFormat('es-CL').format(params.value),
      sortable: true,
      filter: 'agNumberColumnFilter',
      resizable: true
    },
    { 
      field: 'price', 
      headerName: t('grid.columns.price'), 
      width: 120, 
      type: 'numericColumn', 
      valueFormatter: (params) => params.value.toFixed(4),
      sortable: true,
      filter: 'agNumberColumnFilter',
      resizable: true
    },
    { 
      field: 'status', 
      headerName: t('grid.columns.status'), 
      width: 100, 
      cellRenderer: StatusCellRenderer,
      sortable: true,
      filter: 'agTextColumnFilter',
      resizable: true
    },
    { 
      field: 'confidence', 
      headerName: t('grid.columns.confidence'), 
      width: 100,
      valueFormatter: (params) => `${(params.value * 100).toFixed(0)}%`,
      sortable: true,
      filter: 'agNumberColumnFilter',
      resizable: true
    }
  ], [t]);

  const getContextMenuItems = useCallback((params: GetContextMenuItemsParams): (string | MenuItemDef)[] => [
    {
      name: t('grid.contextMenu.verifyTrade'),
      action: () => {/* Verify trade action */}
    },
    {
      name: t('grid.contextMenu.viewConfirmation'),
      action: () => {/* View confirmation action */}
    },
    {
      name: t('grid.contextMenu.dispute'),
      action: () => {/* Dispute trade action */}
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
        rowData={mockMatchedTrades}
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

export default MatchedTradesGrid;