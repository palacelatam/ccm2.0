import React, { useCallback, useMemo, useState, useEffect, useRef } from 'react';
import { AgGridReact } from 'ag-grid-react';
import { ColDef, GetContextMenuItemsParams, MenuItemDef } from 'ag-grid-community';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../auth/AuthContext';
import { clientService, EmailConfirmation, ClientService } from '../../services/clientService';
import StatusCellRenderer from './StatusCellRenderer';
import Toast from '../common/Toast';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';
import './TradeGrid.css';

// Using v1.0 field structure for email confirmations with extracted trade data

interface ConfirmationsGridProps {
  onDataChange?: () => void;
  refreshTrigger?: number;
  selectedMatchId?: string | null;
  onRowClick?: (matchId: string | null) => void;
}

const ConfirmationsGrid: React.FC<ConfirmationsGridProps> = ({ 
  onDataChange, 
  refreshTrigger,
  selectedMatchId,
  onRowClick
}) => {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [emails, setEmails] = useState<EmailConfirmation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState<string | null>(null);
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState<string>('');
  const [toastType, setToastType] = useState<'success' | 'error' | 'info' | 'warning'>('success');
  const fileInputRef = useRef<HTMLInputElement>(null);
  const gridRef = useRef<AgGridReact>(null);

  // Get client ID from user context
  const clientId = user?.organization?.id || user?.id;

  // Helper function to show toast notifications
  const showToastNotification = (message: string, type: 'success' | 'error' | 'info' | 'warning' = 'success') => {
    setToastMessage(message);
    setToastType(type);
    setShowToast(true);
  };

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

  const loadEmails = useCallback(async (preserveGridState = false) => {
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
      const emailsData = await clientService.getAllEmailConfirmations(clientId);
      
      if (preserveGridState && gridRef.current?.api) {
        // Update data while preserving grid state (sorting, filtering, etc.)
        gridRef.current.api.setRowData(emailsData);
      } else {
        // Full reload (initial load)
        setEmails(emailsData);
      }
    } catch (error) {
      console.error('Error loading email confirmations:', error);
      setError(error instanceof Error ? error.message : 'Failed to load email confirmations');
    } finally {
      if (!preserveGridState) {
        setLoading(false);
      }
    }
  }, [clientId]);

  // Load emails on mount and when client changes
  useEffect(() => {
    loadEmails();
  }, [loadEmails]);

  // Refresh when refreshTrigger changes (called by parent)
  useEffect(() => {
    if (refreshTrigger && refreshTrigger > 0) {
      loadEmails(true); // Preserve grid state on refresh
    }
  }, [refreshTrigger, loadEmails]);
  
  // Refresh cell styles when selectedMatchId changes to update row highlighting
  useEffect(() => {
    if (gridRef.current?.api) {
      // Use redrawRows() instead of refreshCells() to trigger getRowStyle recalculation
      gridRef.current.api.redrawRows();
    }
  }, [selectedMatchId]);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file || !clientId) {
      if (!clientId) setUploadMessage(t('grid.messages.noClientId'));
      return;
    }

    // Validate file type
    if (!file.name.toLowerCase().endsWith('.msg') && !file.name.toLowerCase().endsWith('.pdf')) {
      const errorMessage = 'Please select an MSG or PDF file';
      setUploadMessage(errorMessage);
      showToastNotification(errorMessage, 'warning');
      return;
    }

    setUploading(true);
    setUploadMessage(null);

    try {
      const result = await clientService.uploadEmailFile(clientId, file);
      
      // Refresh the emails data while preserving grid state
      await loadEmails(true);
      
      // Notify parent component to refresh other grids
      if (onDataChange) {
        onDataChange();
      }
      
      // Show appropriate toast based on results
      const tradesCount = result.trades_extracted || 0;
      const matchesCount = result.matches_found || 0;
      const duplicatesCount = result.duplicates_found || 0;
      
      // Use the enhanced data from the backend response
      const counterpartyName = result.counterparty_name || 'Unknown';
      const clientTradeNumbers = (result.matched_trade_numbers && result.matched_trade_numbers.length > 0) ? 
        ` (${result.matched_trade_numbers.join(', ')})` : '';
      
      // Determine toast type and message based on duplicates
      let toastType: 'success' | 'warning' | 'error' = 'success';
      let message = '';
      
      if (duplicatesCount > 0) {
        toastType = 'warning';
        const duplicateWord = duplicatesCount === 1 ? 'duplicate' : 'duplicates';
        message = `Warning: ${duplicatesCount} ${duplicateWord} detected in email from ${counterpartyName}. These trades were already processed previously. ${matchesCount} new matches created${clientTradeNumbers}`;
      } else {
        message = `Successfully processed email file from ${counterpartyName} with ${tradesCount} trades extracted and ${matchesCount} matches found${clientTradeNumbers}`;
      }
      
      showToastNotification(message, toastType);
      setUploadMessage(null);
      
    } catch (error) {
      console.error('Upload error:', error);
      const errorMessage = error instanceof Error ? error.message : 'Upload failed';
      setUploadMessage(errorMessage);
      showToastNotification(errorMessage, 'error');
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
          case 'Matched':
            color = '#4CAF50'; // Same as Confirmation OK
            break;
          case 'Duplicate':
            color = '#FFA500'; // Orange for duplicates
            break;
          default:
            color = '#FFFFFF'; // Default fallback
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
      width: 100,
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
      field: 'ForwardPrice', 
      width: 120,
      cellRenderer: (params: any) => {
        const value = params.value || 0;
        const formattedValue = value.toLocaleString('en-US', {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2
        });
        
        const differingFields = params.data?.differingFields || [];
        const hasDifference = differingFields.includes('ForwardPrice');
        
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
    const matchId = event.data?.matchId || event.data?.match_id || null;
    
    if (onRowClick) {
      onRowClick(matchId);
    }
  }, [onRowClick]);

  // Row styling for highlighting
  const getRowStyle = useCallback((params: any) => {
    // Check both possible field names for match_id
    const matchId = params.data?.matchId || params.data?.match_id;
    
    if (selectedMatchId && matchId && matchId === selectedMatchId) {
      return { backgroundColor: '#264a73' }; // Highlight color for selected row
    }
    return undefined;
  }, [selectedMatchId]);

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
              onClick={triggerFileUpload}
              disabled={uploading}
              title={uploading ? 'Uploading...' : 'Upload MSG/PDF email file'}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: '36px',
                height: '36px',
                background: 'transparent',
                border: 'none',
                borderRadius: '6px',
                cursor: uploading ? 'not-allowed' : 'pointer',
                opacity: uploading ? 0.5 : 1,
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
            
            <input
              ref={fileInputRef}
              type="file"
              accept=".msg,.pdf"
              onChange={handleFileUpload}
              style={{ display: 'none' }}
            />
          </div>
        </div>
      </div>

      {/* Grid Content */}
      {emails.length === 0 ? (
        <div className="empty-state" style={{ flex: '1', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#b3b3b3' }}>
          No email confirmations found. Upload MSG or PDF email files to get started.
        </div>
      ) : (
        <div className="ag-theme-alpine-dark trade-grid" style={{ flex: '1', minHeight: 0, height: '100%' }}>
          <AgGridReact
            ref={gridRef}
            rowData={emails}
            columnDefs={columnDefs}
            getContextMenuItems={getContextMenuItems}
            onRowClicked={handleRowClick}
            getRowStyle={getRowStyle}
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
      
      {/* Toast Notification */}
      <Toast
        message={toastMessage}
        type={toastType}
        isVisible={showToast}
        onClose={() => setShowToast(false)}
        duration={4000}
      />
    </div>
  );
};

export default ConfirmationsGrid;