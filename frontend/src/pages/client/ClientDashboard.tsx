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
  
  // Toast state for real-time notifications
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState<string>('');
  const [toastType, setToastType] = useState<'success' | 'error' | 'info' | 'warning'>('success');

  // Get client ID from user context
  const clientId = user?.organization?.id || user?.id;
  
  // DEBUG: Show what client ID we're actually getting
  console.log('🔍 [ClientDashboard] User object:', user);
  console.log('🔍 [ClientDashboard] Derived clientId:', clientId);
  console.log('🔍 [ClientDashboard] user?.organization?.id:', user?.organization?.id);
  console.log('🔍 [ClientDashboard] user?.id:', user?.id);

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

  // Connect to real-time event stream - SIMPLE VERSION WITH EVENT HANDLING
  const { status } = useEventStreamSimple({
    clientId: clientId, // Use the actual user's client ID
    onEvent: (eventData) => {
      console.log('🎉 [ClientDashboard] Received event:', eventData.type, eventData.title);
      
      // Show toast notification
      showToastNotification(
        `${eventData.title}: ${eventData.message}`,
        eventData.type === 'duplicate_detected' ? 'warning' : 'success'
      );
      
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

  return (
    <div className="dashboard-container">
      <div className={`top-panels ${isBottomPanelExpanded ? '' : 'expanded'}`}>
        <div className="top-left-panel">
          <h3>{t('dashboard.matchedTrades')}</h3>
          <MatchedTradesGrid refreshTrigger={refreshTrigger} />
        </div>
        <div className="top-right-panel">
          <h3>{t('dashboard.confirmations')}</h3>
          <ConfirmationsGrid onDataChange={triggerGridRefresh} refreshTrigger={refreshTrigger} />
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