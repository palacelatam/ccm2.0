import React, { useCallback, useMemo, useState, useEffect, useRef } from 'react';
import { AgGridReact } from 'ag-grid-react';
import { ColDef, GetContextMenuItemsParams, MenuItemDef } from 'ag-grid-community';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../auth/AuthContext';
import { clientService, ClientService } from '../../services/clientService';
import StatusCellRenderer from './StatusCellRenderer';
import AlertModal from '../common/AlertModal';
import InlineMenu, { InlineMenuItem } from '../common/InlineMenu';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';
import './TradeGrid.css';

// Using v1.0 field structure directly

interface ClientTradesGridProps {
  refreshTrigger?: number;
}

const ClientTradesGrid: React.FC<ClientTradesGridProps> = ({ refreshTrigger }) => {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [trades, setTrades] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState<string | null>(null);
  const [overwriteData, setOverwriteData] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const [successData, setSuccessData] = useState<{tradesCount: number, message: string} | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const gridRef = useRef<AgGridReact>(null);

  // Inline menu state for right-click functionality
  const [showInlineMenu, setShowInlineMenu] = useState(false);
  const [inlineMenuPosition, setInlineMenuPosition] = useState({ x: 0, y: 0 });
  const [selectedTradeForMenu, setSelectedTradeForMenu] = useState<any | null>(null);

  // Get client ID from user context (assuming user has organization data)
  const clientId = user?.organization?.id || user?.id;

  const loadTrades = useCallback(async (preserveGridState = false) => {
    if (!clientId) {
      setLoading(false);
      setError(t('grid.messages.noClientId'));
      return;
    }

    try {
      if (!preserveGridState) {
        setLoading(true);
      }
      setError(null);
      const tradesData = await clientService.getUnmatchedTrades(clientId);
      
      if (preserveGridState && gridRef.current?.api) {
        // Update data while preserving grid state (sorting, filtering, etc.)
        gridRef.current.api.setRowData(tradesData);
      } else {
        // Full reload (initial load)
        setTrades(tradesData);
      }
    } catch (error) {
      console.error('Error loading trades:', error);
      setError(error instanceof Error ? error.message : t('grid.messages.uploadFailed'));
    } finally {
      if (!preserveGridState) {
        setLoading(false);
      }
    }
  }, [clientId, t]);

  // Load trades on mount and when client changes
  useEffect(() => {
    loadTrades();
  }, [loadTrades]);

  // Refresh when refreshTrigger changes (called by parent)
  useEffect(() => {
    if (refreshTrigger && refreshTrigger > 0) {
      loadTrades(true); // Preserve grid state on refresh
    }
  }, [refreshTrigger, loadTrades]);

  // Add native context menu handler for status column
  useEffect(() => {
    const handleContextMenu = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      // Check if the clicked element is within a trade_status column cell
      const cellElement = target.closest('[col-id="trade_status"]');

      if (cellElement) {
        e.preventDefault();
        e.stopPropagation();

        // Find the row node to get the data
        const rowElement = cellElement.closest('[role="row"]');
        if (rowElement && gridRef.current?.api) {
          const rowIndex = rowElement.getAttribute('row-index');
          if (rowIndex) {
            const rowNode = gridRef.current.api.getDisplayedRowAtIndex(parseInt(rowIndex));
            if (rowNode) {
              setSelectedTradeForMenu(rowNode.data);
              setInlineMenuPosition({ x: e.clientX, y: e.clientY });
              setShowInlineMenu(true);
            }
          }
        }
      }
    };

    // Add the event listener
    document.addEventListener('contextmenu', handleContextMenu);

    // Cleanup
    return () => {
      document.removeEventListener('contextmenu', handleContextMenu);
    };
  }, [trades]); // Re-attach when trades change
  
  const columnDefs: ColDef[] = useMemo(() => [
    {
      headerName: t('grid.columns.status'),
      field: 'status',  // Keep this as 'status' to read the correct data field
      colId: 'trade_status',  // Use a unique column ID to avoid conflicts
      width: 150,
      sortable: true,
      filter: true,
      cellRenderer: StatusCellRenderer
    },
    { 
      headerName: t('grid.columns.tradeNumber'), 
      field: 'TradeNumber', 
      width: 90, 
      sortable: true, 
      filter: true,
      sort: 'asc',
      sortIndex: 0
    },
    { 
      headerName: t('grid.columns.counterparty'), 
      field: 'CounterpartyName', 
      width: 140, 
      sortable: true, 
      filter: true 
    },
    { 
      headerName: t('grid.columns.productType'), 
      field: 'ProductType', 
      width: 90, 
      sortable: true, 
      filter: true 
    },
    { 
      headerName: t('grid.columns.tradeDate'), 
      field: 'TradeDate', 
      width: 130,
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
      width: 130,
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
      width: 70, 
      sortable: true, 
      filter: true 
    },
    { 
      headerName: t('grid.columns.currency1'), 
      field: 'Currency1', 
      width: 70, 
      sortable: true, 
      filter: true 
    },
    { 
      headerName: t('grid.columns.amount'), 
      field: 'QuantityCurrency1', 
      width: 130, 
      sortable: true, 
      filter: true, 
      valueFormatter: (params) => {
        const value = params.value || 0;
        return value.toLocaleString('en-US', {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2
        });
      }
    },
    { 
      headerName: t('grid.columns.price'), 
      field: 'Price', 
      width: 100, 
      sortable: true, 
      filter: true, 
      valueFormatter: (params) => {
        const value = params.value || 0;
        return value.toLocaleString('en-US', {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2
        });
      }
    },
    { 
      headerName: t('grid.columns.currency2'), 
      field: 'Currency2', 
      width: 70, 
      sortable: true, 
      filter: true 
    },
    { 
      headerName: t('grid.columns.maturityDate'), 
      field: 'MaturityDate', 
      width: 130,
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
      width: 120, 
      sortable: true, 
      filter: true 
    },
    { 
      headerName: t('grid.columns.settlementType'), 
      field: 'SettlementType', 
      width: 130, 
      sortable: true, 
      filter: true 
    },
    { 
      headerName: t('grid.columns.settlementCurrency'), 
      field: 'SettlementCurrency', 
      width: 120, 
      sortable: true, 
      filter: true 
    },
    { 
      headerName: t('grid.columns.paymentDate'), 
      field: 'PaymentDate', 
      width: 130,
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
      width: 160, 
      sortable: true, 
      filter: true 
    },
    { 
      headerName: t('grid.columns.ourPaymentMethod'), 
      field: 'OurPaymentMethod', 
      width: 140, 
      sortable: true, 
      filter: true 
    }
  ], [t]);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file || !clientId) {
      if (!clientId) setUploadMessage(t('grid.messages.noClientId'));
      return;
    }

    // Validate file type
    if (!file.name.toLowerCase().endsWith('.csv')) {
      setUploadMessage(t('grid.messages.selectCsvFile'));
      return;
    }

    setUploading(true);
    setUploadMessage(null);

    try {
      // Use existing clientService method with overwrite parameter
      const result = await clientService.uploadTradeFileWithOverwrite(clientId, file, overwriteData);
      
      // Refresh the trades data while preserving grid state
      await loadTrades(true);
      
      // Show success modal
      setSuccessData({
        tradesCount: result.records_processed,
        message: `${t('grid.messages.successfullyProcessed').replace('{count}', result.records_processed.toString())}`
      });
      setShowSuccessModal(true);
      setUploadMessage(null); // Clear any previous messages
      
    } catch (error) {
      console.error('Upload error:', error);
      setUploadMessage(error instanceof Error ? error.message : t('grid.messages.uploadFailed'));
      setShowSuccessModal(false);
    } finally {
      setUploading(false);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const triggerFileUpload = () => {
    fileInputRef.current?.click();
  };

  const handleDeleteAllTrades = async () => {
    if (!clientId) {
      setUploadMessage(t('grid.messages.noClientId'));
      return;
    }

    const confirmed = window.confirm(t('grid.messages.confirmDeleteTrades'));
    if (!confirmed) return;

    setDeleting(true);
    setUploadMessage(null);

    try {
      // Use the real delete endpoint
      const result = await clientService.deleteAllUnmatchedTrades(clientId);
      
      // Refresh the trades data from database while preserving grid state
      await loadTrades(true);
      
      setSuccessData({
        tradesCount: result.trades_deleted,
        message: `${t('grid.messages.successfullyDeleted').replace('{count}', result.trades_deleted.toString())}`
      });
      setShowSuccessModal(true);
      setUploadMessage(null);
      
    } catch (error) {
      console.error('Delete error:', error);
      setUploadMessage(error instanceof Error ? error.message : t('grid.messages.deleteFailed'));
      setShowSuccessModal(false);
    } finally {
      setDeleting(false);
    }
  };

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
        <div className="loading-message">{t('grid.messages.loading')}</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="ag-theme-alpine-dark trade-grid error-state">
        <div className="error-message">
          {t('grid.messages.errorLoading')}: {error}
          <button 
            onClick={() => window.location.reload()} 
            className="retry-button"
          >
            {t('grid.messages.retry')}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ height: '100%', width: '100%', display: 'flex', flexDirection: 'column', minHeight: 0 }}>
      {/* Upload Controls */}
      <div className="grid-header-controls" style={{ 
        display: 'flex', 
        justifyContent: 'flex-end', 
        alignItems: 'center', 
        borderBottom: '1px solid #333',
        marginTop: '-16px',
        marginBottom: '8px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          {uploadMessage && (
            <div style={{ 
              color: uploadMessage.includes('Successfully') ? '#28a745' : '#dc3545',
              fontSize: '14px',
              marginRight: '15px'
            }}>
              {uploadMessage}
            </div>
          )}
          
          <div className="upload-controls" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <button 
              onClick={handleDeleteAllTrades}
              disabled={uploading || deleting || trades.length === 0}
              title={deleting ? t('grid.messages.deleting') : t('grid.messages.deleteAllUnmatched')}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: '36px',
                height: '36px',
                background: 'transparent',
                border: 'none',
                borderRadius: '6px',
                cursor: (uploading || deleting || trades.length === 0) ? 'not-allowed' : 'pointer',
                opacity: (uploading || deleting || trades.length === 0) ? 0.5 : 1,
                transition: 'opacity 0.2s ease'
              }}
            >
              {deleting ? (
                <span style={{ fontSize: '16px' }}>⏳</span>
              ) : (
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#4a9eff" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" style={{ width: '16px', height: '16px' }}>
                  <path d="M3 6h18" />
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6" />
                  <path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                </svg>
              )}
            </button>
            
            <button 
              onClick={triggerFileUpload}
              disabled={uploading || deleting}
              title={uploading ? t('grid.messages.uploading') : t('grid.messages.uploadCsvFile')}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: '36px',
                height: '36px',
                background: 'transparent',
                border: 'none',
                borderRadius: '6px',
                cursor: (uploading || deleting) ? 'not-allowed' : 'pointer',
                opacity: (uploading || deleting) ? 0.5 : 1,
                transition: 'opacity 0.2s ease'
              }}
            >
              {uploading ? (
                <span style={{ fontSize: '16px' }}>⏳</span>
              ) : (
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#4a9eff" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" style={{ width: '16px', height: '16px' }}>
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                  <polyline points="17 8 12 3 7 8" />
                  <line x1="12" y1="3" x2="12" y2="15" />
                </svg>
              )}
            </button>
            
            <label style={{ display: 'flex', alignItems: 'center', gap: '5px', color: '#fff', fontSize: '14px', whiteSpace: 'nowrap' }}>
              <input 
                type="checkbox" 
                checked={overwriteData}
                onChange={(e) => setOverwriteData(e.target.checked)}
                disabled={uploading || deleting}
              />
              {t('grid.messages.overwriteExistingTrades')}
            </label>
            
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv"
              onChange={handleFileUpload}
              style={{ display: 'none' }}
            />
          </div>
        </div>
      </div>

      {/* Grid Content */}
      {trades.length === 0 ? (
        <div className="empty-state" style={{ flex: '1', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#b3b3b3' }}>
          {t('grid.messages.noTradesFound')}
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
            domLayout="normal"
            defaultColDef={{
              sortable: true,
              filter: true,
              resizable: true,
              minWidth: 80
            }}
            sortingOrder={['asc', 'desc']}
          />
        </div>
      )}
      
      {/* Success Modal */}
      {showSuccessModal && successData && (
        <AlertModal
          isOpen={showSuccessModal}
          onClose={() => setShowSuccessModal(false)}
          title={t('grid.messages.uploadSuccessful')}
          message={successData.message}
          type="success"
        />
      )}

      {/* Inline Menu for right-click */}
      {showInlineMenu && selectedTradeForMenu && (
        <InlineMenu
          position={inlineMenuPosition}
          onClose={() => setShowInlineMenu(false)}
          items={(() => {
            const menuItems: (InlineMenuItem | 'separator')[] = [];

            // Only show "Confirmed Via Portal" if status is "unmatched"
            if (selectedTradeForMenu.status?.toLowerCase() === 'unmatched') {
              menuItems.push({
                label: t('grid.contextMenu.confirmedViaPortal'),
                action: () => {
                  // Test alert to confirm the click is working
                  alert(`Button clicked! Trade Number: ${selectedTradeForMenu.TradeNumber || 'Unknown'}`);
                  console.log('Confirmed Via Portal clicked for trade:', selectedTradeForMenu);
                  setShowInlineMenu(false);
                }
              });
            }

            // Return the menu items (or empty array if no applicable items)
            return menuItems.length > 0 ? menuItems : [
              {
                label: 'No actions available',
                action: () => {},
                disabled: true
              }
            ];
          })()}
        />
      )}
    </div>
  );
};

export default ClientTradesGrid;