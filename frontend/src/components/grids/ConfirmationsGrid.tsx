import React, { useCallback, useMemo, useState, useEffect, useRef } from 'react';
import { AgGridReact } from 'ag-grid-react';
import { ColDef, GetContextMenuItemsParams, MenuItemDef, CellContextMenuEvent } from 'ag-grid-community';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../auth/AuthContext';
import { clientService, EmailConfirmation, ClientService } from '../../services/clientService';
import StatusCellRenderer from './StatusCellRenderer';
import Toast from '../common/Toast';
import InlineMenu, { InlineMenuItem } from '../common/InlineMenu';
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

  // Inline menu state
  const [showInlineMenu, setShowInlineMenu] = useState(false);
  const [inlineMenuPosition, setInlineMenuPosition] = useState({ x: 0, y: 0 });
  const [selectedEmailForMenu, setSelectedEmailForMenu] = useState<any | null>(null);
  const [statusHistory, setStatusHistory] = useState<Map<string, string>>(new Map());
  
  // Settlement instruction dialog state
  const [showSettlementDialog, setShowSettlementDialog] = useState(false);
  const [settlementDialogTrade, setSettlementDialogTrade] = useState<any | null>(null);
  
  // Settlement instruction loading state
  const [generatingSettlementInstructions, setGeneratingSettlementInstructions] = useState<Set<string>>(new Set());

  // Get client ID from user context
  const clientId = user?.organization?.id || user?.id;
  const organizationName = user?.organization?.name || 'Company';


  // Helper function to show toast notifications
  const showToastNotification = (message: string, type: 'success' | 'error' | 'info' | 'warning' = 'success') => {
    setToastMessage(message);
    setToastType(type);
    setShowToast(true);
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
      
      // Load both email confirmations and matched trades
      const [emailsData, matchedTradesData] = await Promise.all([
        clientService.getAllEmailConfirmations(clientId),
        clientService.getMatchedTrades(clientId)
      ]);
      
      // Enhance email confirmations with differingFields from matched trades
      const enhancedEmails = emailsData.map(email => {
        if (email.matchId) {
          // Find the corresponding matched trade
          const matchedTrade = matchedTradesData.find(trade => 
            trade.matchId === email.matchId || trade.match_id === email.matchId
          );
          
          if (matchedTrade && matchedTrade.differingFields) {
            return {
              ...email,
              differingFields: matchedTrade.differingFields
            };
          }
        }
        
        // Return email without differingFields if no match found
        return {
          ...email,
          differingFields: []
        };
      });
      
      if (preserveGridState && gridRef.current?.api) {
        // Update data while preserving grid state (sorting, filtering, etc.)
        gridRef.current.api.setRowData(enhancedEmails);
      } else {
        // Full reload (initial load)
        setEmails(enhancedEmails);
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

  // Add native context menu handler for status column
  useEffect(() => {
    const handleContextMenu = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      // Check if the clicked element is within a status column cell
      const cellElement = target.closest('[col-id="status"]');
      
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
              setSelectedEmailForMenu(rowNode.data);
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
  }, [emails]); // Re-attach when emails change
  

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

  // Handle status update
  const handleStatusUpdate = async (emailId: string, newStatus: string) => {
    try {
      // Store the current status in history for undo
      const currentEmail = emails.find(e => e.id === emailId);
      if (currentEmail) {
        setStatusHistory(prev => new Map(prev).set(emailId, currentEmail.status));
      }

      // Update locally first for immediate UI feedback
      setEmails(prevEmails => 
        prevEmails.map(email => 
          email.id === emailId ? { ...email, status: newStatus } : email
        )
      );

      // Update in the grid if it exists
      if (gridRef.current?.api) {
        gridRef.current.api.forEachNode((node) => {
          if (node.data.id === emailId) {
            node.setDataValue('status', newStatus);
          }
        });
      }

      // Call API to persist the change
      if (clientId) {
        await clientService.updateEmailConfirmationStatus(clientId, emailId, newStatus);
        showToastNotification(`Status updated to ${newStatus}`, 'success');
      }
    } catch (error) {
      console.error('Error updating status:', error);
      showToastNotification('Failed to update status', 'error');
      // Revert on error
      await loadEmails(true);
    }
  };

  // Handle undo status
  const handleUndoStatus = async (emailId: string) => {
    const previousStatus = statusHistory.get(emailId);
    if (previousStatus) {
      await handleStatusUpdate(emailId, previousStatus);
      // Remove from history after undo
      setStatusHistory(prev => {
        const newMap = new Map(prev);
        newMap.delete(emailId);
        return newMap;
      });
    }
  };

  // Generate mailback email
  const generateMailback = async (emailData: any) => {
    const counterpartyName = emailData.CounterpartyName || emailData.EmailSender || 'Counterparty';
    const tradeNumber = emailData.BankTradeNumber || emailData.id;
    const toEmail = emailData.EmailSender || '';
    const ccEmail = 'confirmaciones_dev@servicios.palace.cl';
    
    // Get discrepancy information from matched trade data using matchId
    let hasActualDiscrepancies = false;
    let discrepancyFields = [];
    let matchedTradeData: any = null;
    
    if (emailData.matchId && clientId) {
      try {
        // Fetch the matched trades to get the discrepancy information
        const matchedTrades = await clientService.getMatchedTrades(clientId);
        matchedTradeData = matchedTrades.find(trade => trade.matchId === emailData.matchId || trade.match_id === emailData.matchId);
        
        if (matchedTradeData && matchedTradeData.differingFields && matchedTradeData.differingFields.length > 0) {
          hasActualDiscrepancies = true;
          discrepancyFields = matchedTradeData.differingFields;
        }
      } catch (error) {
        console.error('Error fetching matched trade data for mailback:', error);
        // Fallback to checking status if we can't get matched trade data
        if (emailData.status === 'Difference') {
          hasActualDiscrepancies = true;
          discrepancyFields = ['Multiple fields'];
        }
      }
    }
    
    let body = '';
    if (hasActualDiscrepancies) {
      // Email with discrepancies
      body = t('mailback.greeting', { counterpartyName }) + '\n\n';
      body += t('mailback.discrepancyIntro', { tradeNumber, organizationName }) + '\n\n';
      
      // Add each discrepancy
      discrepancyFields.forEach((field: string) => {
        const emailValue = emailData[field] || 'N/A';
        const clientValue = matchedTradeData ? (matchedTradeData[field] || 'N/A') : 'N/A';
        
        // Debug logging
        console.log('DEBUG Mailback:', {
          field,
          emailValue,
          clientValue,
          matchedTradeDataKeys: matchedTradeData ? Object.keys(matchedTradeData) : 'null',
          emailDataKeys: Object.keys(emailData)
        });
        
        body += `${field}:\n`;
        body += t('mailback.yourValue') + `: ${emailValue}\n`;
        body += t('mailback.ourValue') + `: ${clientValue}\n\n`;
      });
      
      body += t('mailback.regards') + ',\n' + organizationName;
    } else {
      // Confirmation email (no discrepancies)
      body = t('mailback.greeting', { counterpartyName }) + '\n\n';
      body += t('mailback.confirmationMessage', { tradeNumber, organizationName }) + '\n\n';
      body += t('mailback.regards') + ',\n' + organizationName;
    }
    
    // Encode for mailto link
    const subject = encodeURIComponent(t('mailback.subject', { tradeNumber }));
    const encodedBody = encodeURIComponent(body);
    const mailtoLink = `mailto:${toEmail}?cc=${ccEmail}&subject=${subject}&body=${encodedBody}`;
    
    // Open email client
    window.location.href = mailtoLink;
  };

  // Generate settlement instruction document
  const generateSettlementInstruction = async (emailData: any) => {
    const emailId = emailData.id;
    
    try {
      if (!clientId) {
        throw new Error('Client ID not available');
      }
      
      // Set loading state
      setGeneratingSettlementInstructions(prev => {
        const newSet = new Set([...prev, emailId]);
        
        // Force AG Grid to refresh just this specific cell
        // Use a small delay to ensure React state has updated
        setTimeout(() => {
          if (gridRef.current?.api) {
            gridRef.current.api.refreshCells({
              columns: ['settlementInstructionDocument'],
              force: true
            });
          }
        }, 10); // Small delay to ensure state is updated
        
        return newSet;
      });
      
      // Get client trade number from matched trade data
      let clientTradeNumber = emailData.BankTradeNumber; // Fallback
      
      if (emailData.matchId && clientId) {
        try {
          const matchedTrades = await clientService.getMatchedTrades(clientId);
          const matchedTrade = matchedTrades.find(trade => trade.matchId === emailData.matchId || trade.match_id === emailData.matchId);
          
          if (matchedTrade && matchedTrade.TradeNumber) {
            clientTradeNumber = matchedTrade.TradeNumber;
          }
        } catch (error) {
          console.error('Error fetching client trade number:', error);
        }
      }
      
      // Call backend service to generate settlement instruction
      const result = await clientService.generateSettlementInstruction(
        clientId, 
        clientTradeNumber, 
        emailData.BankTradeNumber
      );
      
      console.log('Settlement instruction generation result:', result);
      
      if (result.success) {
        showToastNotification(t('grid.messages.settlementInstructionGenerated', { tradeNumber: clientTradeNumber }), 'success');
        // Note: Paperclip will appear after Step 4 (cloud storage upload)
      } else {
        throw new Error(result.message || 'Failed to generate settlement instruction');
      }
      
    } catch (error) {
      console.error('Error generating settlement instruction:', error);
      showToastNotification(t('grid.messages.settlementInstructionFailed'), 'error');
    } finally {
      // Clear loading state
      setGeneratingSettlementInstructions(prev => {
        const newSet = new Set(prev);
        newSet.delete(emailId);
        
        // Force AG Grid to refresh just this specific cell
        setTimeout(() => {
          if (gridRef.current?.api) {
            const rowNode = gridRef.current.api.getRowNode(emailId);
            if (rowNode) {
              gridRef.current.api.refreshCells({
                rowNodes: [rowNode],
                columns: ['settlementInstructionDocument'],
                force: true
              });
              console.log('Cleared loading state and refreshed cell for email:', emailId);
            }
          }
        }, 0);
        
        return newSet;
      });
    }
  };

  // Handle mailback with optional settlement instruction
  const handleMailbackWithSettlement = async (emailData: any, includeSettlement: boolean = false) => {
    if (includeSettlement && emailData.status === 'Confirmation OK') {
      // Generate settlement instruction first
      await generateSettlementInstruction(emailData);
    }
    
    // Then proceed with normal mailback
    await generateMailback(emailData);
  };

  // Show settlement instruction dialog for mailback
  const showSettlementInstructionDialog = async (emailData: any) => {
    // Get client trade number for display
    let clientTradeNumber = emailData.BankTradeNumber; // Fallback
    
    if (emailData.matchId && clientId) {
      try {
        const matchedTrades = await clientService.getMatchedTrades(clientId);
        const matchedTrade = matchedTrades.find(trade => trade.matchId === emailData.matchId || trade.match_id === emailData.matchId);
        
        if (matchedTrade && matchedTrade.TradeNumber) {
          clientTradeNumber = matchedTrade.TradeNumber;
        }
      } catch (error) {
        console.error('Error fetching client trade number for dialog:', error);
      }
    }
    
    setSettlementDialogTrade({...emailData, clientTradeNumber});
    setShowSettlementDialog(true);
    setShowInlineMenu(false);
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
      cellRenderer: (params: any): React.ReactElement => {
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
            color = '#00e7ff'; // Light blue for Resolved
            break;
          case 'Tagged':
            color = '#FFA500'; // Orange for Tagged
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
      },
      onCellContextMenu: (params: any) => {
        // Prevent default context menu
        if (params.event) {
          params.event.preventDefault();
          params.event.stopPropagation();
        }
        
        // Set the selected email data
        setSelectedEmailForMenu(params.data);
        
        // Set the position for the inline menu
        setInlineMenuPosition({
          x: params.event.clientX,
          y: params.event.clientY
        });
        
        // Show the inline menu
        setShowInlineMenu(true);
        
        // Return false to prevent AG Grid's default behavior
        return false;
      }
    },
    {
      headerName: t('grid.columns.cartaInstruccion'),
      field: 'settlementInstructionDocument',
      width: 80,
      sortable: false,
      filter: false,
      cellRenderer: (params: any) => {
        const emailId = params.data?.id;
        const isGenerating = generatingSettlementInstructions.has(emailId);
        const documentStatus = isGenerating ? 'generating' : (params.value?.status || 'empty');
        const documentUrl = params.value?.url;
        
        
        let icon = '';
        let tooltip = '';
        let clickable = false;
        let color = '#b3b3b3';
        
        switch(documentStatus) {
          case 'generated':
            icon = '📎';
            tooltip = t('grid.tooltips.cartaInstruccion.generated');
            clickable = true;
            color = '#28a745';
            break;
          case 'generating':
            icon = '⏳';
            tooltip = t('grid.tooltips.cartaInstruccion.generating');
            color = '#ffc107';
            break;
          case 'failed':
            icon = '❌';
            tooltip = t('grid.tooltips.cartaInstruccion.failed');
            clickable = true;
            color = '#dc3545';
            break;
          default:
            return React.createElement('div', {
              style: {
                width: '100%',
                height: '100%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }
            }, '');
        }
        
        const handleClick = () => {
          if (!clickable) return;
          
          if (documentStatus === 'generated' && documentUrl) {
            // Download document
            window.open(documentUrl, '_blank');
          } else if (documentStatus === 'failed') {
            // TODO: Retry generation (will be implemented in Phase 3)
            console.log('Retry settlement instruction generation for trade:', params.data?.BankTradeNumber);
          }
        };
        
        return React.createElement('div', {
          style: {
            width: '100%',
            height: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: clickable ? 'pointer' : 'default',
            color: color,
            fontSize: '16px'
          },
          title: tooltip,
          onClick: handleClick
        }, icon);
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
      width: 150,
      cellRenderer: (params: any) => {
        const value = params.value || '';
        const differingFields = params.data?.differingFields || [];
        const hasDifference = differingFields.includes('CounterpartyName');
        
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
        }, value);
      }
    },
    { 
      headerName: t('grid.columns.productType'), 
      field: 'ProductType', 
      width: 120,
      cellRenderer: (params: any) => {
        const value = params.value || '';
        const differingFields = params.data?.differingFields || [];
        const hasDifference = differingFields.includes('ProductType');
        
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
        }, value);
      }
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
      cellRenderer: (params: any) => {
        const value = params.value || '';
        const formattedValue = value ? (() => {
          const [day, month, year] = value.split('-');
          const date = new Date(year, month - 1, day);
          const dayName = date.toLocaleDateString('es-CL', { weekday: 'short' });
          return `${dayName} ${day}-${month}-${year}`;
        })() : '';
        
        const differingFields = params.data?.differingFields || [];
        const hasDifference = differingFields.includes('ValueDate');
        
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
      headerName: t('grid.columns.direction'), 
      field: 'Direction', 
      width: 100,
      cellRenderer: (params: any) => {
        const value = params.value || '';
        const differingFields = params.data?.differingFields || [];
        const hasDifference = differingFields.includes('Direction');
        
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
        }, value);
      }
    },
    { 
      headerName: t('grid.columns.currency1'), 
      field: 'Currency1', 
      width: 100,
      cellRenderer: (params: any) => {
        const value = params.value || '';
        const differingFields = params.data?.differingFields || [];
        const hasDifference = differingFields.includes('Currency1');
        
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
        }, value);
      }
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
      width: 120,
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
      cellRenderer: (params: any) => {
        const value = params.value || '';
        const differingFields = params.data?.differingFields || [];
        const hasDifference = differingFields.includes('Currency2');
        
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
        }, value);
      }
    },
    { 
      headerName: t('grid.columns.maturityDate'), 
      field: 'MaturityDate', 
      width: 120,
      cellRenderer: (params: any) => {
        const value = params.value || '';
        const formattedValue = value ? (() => {
          const [day, month, year] = value.split('-');
          const date = new Date(year, month - 1, day);
          const dayName = date.toLocaleDateString('es-CL', { weekday: 'short' });
          return `${dayName} ${day}-${month}-${year}`;
        })() : '';
        
        const differingFields = params.data?.differingFields || [];
        const hasDifference = differingFields.includes('MaturityDate');
        
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
      headerName: t('grid.columns.fixingReference'), 
      field: 'FixingReference', 
      width: 140,
      cellRenderer: (params: any) => {
        const value = params.value || '';
        const differingFields = params.data?.differingFields || [];
        const hasDifference = differingFields.includes('FixingReference');
        
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
        }, value);
      }
    },
    { 
      headerName: t('grid.columns.settlementType'), 
      field: 'SettlementType', 
      width: 130,
      cellRenderer: (params: any) => {
        const value = params.value || '';
        const differingFields = params.data?.differingFields || [];
        const hasDifference = differingFields.includes('SettlementType');
        
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
        }, value);
      }
    },
    { 
      headerName: t('grid.columns.settlementCurrency'), 
      field: 'SettlementCurrency', 
      width: 140,
      cellRenderer: (params: any) => {
        const value = params.value || '';
        const differingFields = params.data?.differingFields || [];
        const hasDifference = differingFields.includes('SettlementCurrency');
        
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
        }, value);
      }
    },
    { 
      headerName: t('grid.columns.paymentDate'), 
      field: 'PaymentDate', 
      width: 120,
      cellRenderer: (params: any) => {
        const value = params.value || '';
        const formattedValue = value ? (() => {
          const [day, month, year] = value.split('-');
          const date = new Date(year, month - 1, day);
          const dayName = date.toLocaleDateString('es-CL', { weekday: 'short' });
          return `${dayName} ${day}-${month}-${year}`;
        })() : '';
        
        const differingFields = params.data?.differingFields || [];
        const hasDifference = differingFields.includes('PaymentDate');
        
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
      headerName: t('grid.columns.counterpartyPaymentMethod'), 
      field: 'CounterpartyPaymentMethod', 
      width: 200,
      cellRenderer: (params: any) => {
        const value = params.value || '';
        const differingFields = params.data?.differingFields || [];
        const hasDifference = differingFields.includes('CounterpartyPaymentMethod');
        
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
        }, value);
      }
    },
    { 
      headerName: t('grid.columns.ourPaymentMethod'), 
      field: 'OurPaymentMethod', 
      width: 160,
    }
  ], [t, generatingSettlementInstructions]);

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
            onRowClicked={handleRowClick}
            getRowStyle={getRowStyle}
            onCellContextMenu={(params: any) => {
              // Handle right-click specifically for status column
              if (params.column.getColId() === 'status') {
                if (params.event) {
                  params.event.preventDefault();
                  params.event.stopPropagation();
                }
                
                setSelectedEmailForMenu(params.data);
                setInlineMenuPosition({
                  x: params.event.clientX,
                  y: params.event.clientY
                });
                setShowInlineMenu(true);
              }
            }}
            pagination={true}
            paginationPageSize={50}
            enableRangeSelection={true}
            suppressContextMenu={true}
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
      
      {/* Inline Menu */}
      {showInlineMenu && selectedEmailForMenu && (
        <InlineMenu
            position={inlineMenuPosition}
            onClose={() => setShowInlineMenu(false)}
            items={(() => {
            const baseItems: Array<InlineMenuItem | 'separator'> = [
              {
                label: 'Confirmation OK',
                action: () => handleStatusUpdate(selectedEmailForMenu.id, 'Confirmation OK'),
                disabled: selectedEmailForMenu.status === 'Confirmation OK'
              },
              {
                label: 'Tagged',
                action: () => handleStatusUpdate(selectedEmailForMenu.id, 'Tagged'),
                disabled: selectedEmailForMenu.status === 'Tagged'
              },
              {
                label: 'Resolved',
                action: () => handleStatusUpdate(selectedEmailForMenu.id, 'Resolved'),
                disabled: selectedEmailForMenu.status === 'Resolved'
              },
              {
                label: 'Undo',
                action: () => handleUndoStatus(selectedEmailForMenu.id),
                disabled: !statusHistory.has(selectedEmailForMenu.id)
              },
              'separator',
              {
                label: t('grid.contextMenu.mailback'),
                action: () => {
                  // If status is "Confirmation OK", show dialog to ask about settlement instruction
                  if (selectedEmailForMenu.status === 'Confirmation OK') {
                    showSettlementInstructionDialog(selectedEmailForMenu);
                  } else {
                    // For other statuses, just do normal mailback
                    generateMailback(selectedEmailForMenu);
                  }
                }
              }
            ];

            // Add "Create Settlement Instruction" if conditions are met
            if (selectedEmailForMenu.status === 'Confirmation OK' && 
                (!selectedEmailForMenu.settlementInstructionDocument || 
                 selectedEmailForMenu.settlementInstructionDocument.status === 'empty')) {
              baseItems.push({
                label: t('grid.contextMenu.createSettlementInstruction'),
                action: async () => {
                  setShowInlineMenu(false);
                  await generateSettlementInstruction(selectedEmailForMenu);
                }
              });
            }

            return baseItems;
          })()}
        />
      )}
      
      {/* Settlement Instruction Dialog */}
      {showSettlementDialog && settlementDialogTrade && (
        <div className="modal-overlay">
          <div className="modal settlement-dialog">
            <h3>{t('grid.dialogs.settlementInstruction.title')}</h3>
            <p>{t('grid.dialogs.settlementInstruction.message', { 
              tradeNumber: settlementDialogTrade.clientTradeNumber || settlementDialogTrade.BankTradeNumber || settlementDialogTrade.id 
            })}</p>
            <div className="modal-actions">
              <button 
                className="save-button primary"
                onClick={async () => {
                  setShowSettlementDialog(false);
                  await handleMailbackWithSettlement(settlementDialogTrade, true);
                }}
              >
                {t('grid.dialogs.settlementInstruction.yesButton')}
              </button>
              <button 
                className="save-button secondary"
                onClick={async () => {
                  setShowSettlementDialog(false);
                  await handleMailbackWithSettlement(settlementDialogTrade, false);
                }}
              >
                {t('grid.dialogs.settlementInstruction.noButton')}
              </button>
              <button 
                className="cancel-button"
                onClick={() => setShowSettlementDialog(false)}
              >
                {t('grid.dialogs.settlementInstruction.cancelButton')}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ConfirmationsGrid;