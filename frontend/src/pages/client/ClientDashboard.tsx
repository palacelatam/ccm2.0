import React, { useState, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import MatchedTradesGrid from '../../components/grids/MatchedTradesGrid';
import ConfirmationsGrid from '../../components/grids/ConfirmationsGrid';
import ClientTradesGrid from '../../components/grids/ClientTradesGrid';
import Toast from '../../components/common/Toast';
import { useAuth } from '../../components/auth/AuthContext';
// import useEventStream from '../../hooks/useEventStream';
// import { useEventStreamMinimal } from '../../hooks/useEventStreamMinimal';
import { useEventStreamSimple } from '../../hooks/useEventStreamSimple';

const ClientDashboard: React.FC = () => {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [isBottomPanelExpanded, setIsBottomPanelExpanded] = useState(true);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const confirmationsGridRef = useRef<{ triggerFileUpload: () => void; uploading: boolean }>(null);
  
  // Toast state for real-time notifications
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState<string>('');
  const [toastType, setToastType] = useState<'success' | 'error' | 'info' | 'warning'>('success');
  
  // Row highlighting state for grid linking
  const [selectedMatchId, setSelectedMatchId] = useState<string | null>(null);

  // Get client ID from user context
  const clientId = user?.organization?.id || user?.id;

  // Function to trigger refresh of all grids
  const triggerGridRefresh = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  // Helper function to show toast notifications
  const showToastNotification = (message: string, type: 'success' | 'error' | 'info' | 'warning' = 'success') => {
    setToastMessage(message);
    setToastType(type);
    setShowToast(true);
  };

  // Handlers for grid row highlighting
  const handleMatchedTradeRowClick = (matchId: string | null) => {
    setSelectedMatchId(matchId);
  };

  const handleEmailRowClick = (matchId: string | null) => {
    setSelectedMatchId(matchId);
  };

  const handleUploadClick = () => {
    if (!confirmationsGridRef.current) return;
    
    // Don't allow clicks when uploading
    if (confirmationsGridRef.current.uploading) return;
    
    confirmationsGridRef.current.triggerFileUpload();
  };

  // Connect to real-time event stream - SIMPLE VERSION WITH EVENT HANDLING
  const { status } = useEventStreamSimple({
    clientId: clientId, // Use the actual user's client ID
    onEvent: (eventData) => {
      console.log('🎉 [ClientDashboard] Received event:', eventData.type, eventData.title);
      
      // Check if event is recent (within last 2 minutes) to avoid showing old cached events
      const eventTime = new Date(eventData.timestamp);
      const now = new Date();
      const ageInMinutes = (now.getTime() - eventTime.getTime()) / (1000 * 60);
      
      console.log('🕐 [ClientDashboard] Event age:', ageInMinutes.toFixed(1), 'minutes');
      
      // Only show toast for recent events (less than 2 minutes old)
      if (ageInMinutes < 2) {
        console.log('✅ [ClientDashboard] Showing toast for recent event');
        showToastNotification(
          `${eventData.title}: ${eventData.message}`,
          eventData.type === 'duplicate_detected' ? 'warning' : 'success'
        );
      } else {
        console.log('⏰ [ClientDashboard] Skipping toast for old event (catch-up)');
      }
      
      // Refresh grids for relevant events
      if (eventData.type === 'gmail_processed' || 
          eventData.type === 'trade_matched' || 
          eventData.type === 'match_created' ||
          eventData.action === 'refresh_grids') {
        console.log('🔄 [ClientDashboard] Triggering grid refresh');
        triggerGridRefresh();
      }
    }
  });
  
  // Placeholder values for the status indicator
  const connected = status === 'connected';
  const error = status === 'error' ? 'Connection error' : null;
  
  // Get uploading state from ConfirmationsGrid ref
  const isUploading = confirmationsGridRef.current?.uploading || false;

  return (
    <div className="dashboard-container">
      <div className={`top-panels ${isBottomPanelExpanded ? '' : 'expanded'}`}>
        <div className="top-left-panel">
          <h3>{t('dashboard.matchedTrades')}</h3>
          <MatchedTradesGrid 
            refreshTrigger={refreshTrigger}
            selectedMatchId={selectedMatchId}
            onRowClick={handleMatchedTradeRowClick}
          />
        </div>
        <div className="top-right-panel">
          <h3 style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center'
          }}>
            <span>{t('dashboard.confirmations')}</span>
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              viewBox="0 0 24 24" 
              fill="none" 
              stroke="#4a9eff" 
              strokeWidth="1.8" 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              style={{ width: '16px', height: '16px', cursor: 'pointer' }}
              onClick={handleUploadClick}
            >
              <title>Upload MSG/PDF email file</title>
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="17 8 12 3 7 8" />
              <line x1="12" y1="3" x2="12" y2="15" />
            </svg>
          </h3>
          <ConfirmationsGrid 
            ref={confirmationsGridRef}
            onDataChange={triggerGridRefresh} 
            refreshTrigger={refreshTrigger}
            selectedMatchId={selectedMatchId}
            onRowClick={handleEmailRowClick}
            showTitle={false}
            hideUploadControls={true}
          />
        </div>
      </div>
      <div className={`bottom-panel ${isBottomPanelExpanded ? 'expanded' : 'collapsed'}`}>
        <div className="panel-header">
          <h3>{t('dashboard.clientTrades')}</h3>
          <button 
            className="collapse-button"
            onClick={() => setIsBottomPanelExpanded(!isBottomPanelExpanded)}
            title={isBottomPanelExpanded ? 'Colapsar' : 'Expandir'}
          >
            {isBottomPanelExpanded ? '−' : '+'}
          </button>
        </div>
        {isBottomPanelExpanded && (
          <div className="panel-content">
            <ClientTradesGrid refreshTrigger={refreshTrigger} />
          </div>
        )}
      </div>
      
      {/* Real-time Toast Notifications */}
      <Toast
        message={toastMessage}
        type={toastType}
        isVisible={showToast}
        onClose={() => setShowToast(false)}
        duration={5000}
      />
      
      {/* Event Stream Connection Status (development only) */}
      {process.env.NODE_ENV === 'development' && (
        <div style={{
          position: 'fixed',
          bottom: '10px',
          right: '10px',
          padding: '5px 10px',
          backgroundColor: connected ? '#4CAF50' : error ? '#F44336' : '#FF9800',
          color: 'white',
          borderRadius: '4px',
          fontSize: '12px',
          zIndex: 1000
        }}>
          {connected ? '📡 Connected' : error ? '📡 Error' : '📡 Connecting...'}
          {error && ` (${error})`}
        </div>
      )}
    </div>
  );
};

export default ClientDashboard;