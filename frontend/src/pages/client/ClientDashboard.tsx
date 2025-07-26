import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import MatchedTradesGrid from '../../components/grids/MatchedTradesGrid';
import ConfirmationsGrid from '../../components/grids/ConfirmationsGrid';
import ClientTradesGrid from '../../components/grids/ClientTradesGrid';

const ClientDashboard: React.FC = () => {
  const { t } = useTranslation();
  const [isBottomPanelExpanded, setIsBottomPanelExpanded] = useState(true);

  return (
    <div className="dashboard-container">
      <div className={`top-panels ${isBottomPanelExpanded ? '' : 'expanded'}`}>
        <div className="top-left-panel">
          <h3>{t('dashboard.matchedTrades')}</h3>
          <MatchedTradesGrid />
        </div>
        <div className="top-right-panel">
          <h3>{t('dashboard.confirmations')}</h3>
          <ConfirmationsGrid />
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
            <ClientTradesGrid />
          </div>
        )}
      </div>
    </div>
  );
};

export default ClientDashboard;