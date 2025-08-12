import React, { useCallback, useMemo, useState, useEffect, useRef } from 'react';
import { AgGridReact } from 'ag-grid-react';
import { ColDef, GetContextMenuItemsParams, MenuItemDef } from 'ag-grid-community';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../auth/AuthContext';
import { clientService, EmailConfirmation, ClientService } from '../../services/clientService';
import StatusCellRenderer from './StatusCellRenderer';
import AlertModal from '../common/AlertModal';
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
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState<string | null>(null);
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const [successData, setSuccessData] = useState<{tradesCount: number, message: string} | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

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

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file || !clientId) {
      if (!clientId) setUploadMessage(t('grid.messages.noClientId'));
      return;
    }

    // Validate file type
    if (!file.name.toLowerCase().endsWith('.msg') && !file.name.toLowerCase().endsWith('.pdf')) {
      setUploadMessage('Please select an MSG or PDF file');
      return;
    }

    setUploading(true);
    setUploadMessage(null);

    try {
      const result = await clientService.uploadEmailFile(clientId, file);
      
      // Refresh the emails data
      const emailsData = await clientService.getAllEmailConfirmations(clientId);
      setEmails(emailsData);
      
      // Show success modal
      setSuccessData({
        tradesCount: result.trades_extracted || 0,
        message: `Successfully processed email file with ${result.trades_extracted || 0} trades extracted`
      });
      setShowSuccessModal(true);
      setUploadMessage(null);
      
    } catch (error) {
      console.error('Upload error:', error);
      setUploadMessage(error instanceof Error ? error.message : 'Upload failed');
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
            rowData={emails}
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
          title="Upload Successful"
          message={successData.message}
          type="success"
        />
      )}
    </div>
  );
};

export default ConfirmationsGrid;