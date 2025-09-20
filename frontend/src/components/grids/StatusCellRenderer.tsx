import React from 'react';
import { ICellRendererParams } from 'ag-grid-community';
import { useTranslation } from 'react-i18next';
import './StatusCellRenderer.css';

const StatusCellRenderer: React.FC<ICellRendererParams> = ({ value }) => {
  const { t } = useTranslation();
  const getStatusClass = (status: string) => {
    switch (status?.toUpperCase()) {
      case 'MATCHED':
        return 'status-matched';
      case 'DISPUTED':
        return 'status-disputed';
      case 'UNRECOGNISED':
      case 'UNMATCHED':
        return 'status-unrecognised';
      case 'PENDING':
        return 'status-pending';
      case 'PROCESSED':
        return 'status-processed';
      case 'ERROR':
        return 'status-error';
      case 'CONFIRMED_VIA_PORTAL':
        return 'status-confirmed-portal';
      default:
        return 'status-default';
    }
  };

  const getStatusText = (status: string) => {
    const statusKey = status?.toLowerCase();
    switch (statusKey) {
      case 'matched':
        return t('grid.status.matched');
      case 'disputed':
        return t('grid.status.disputed');
      case 'unrecognised':
        return t('grid.status.unrecognised');
      case 'unmatched':
        return t('grid.status.unmatched');
      case 'pending':
        return t('grid.status.pending');
      case 'processed':
        return t('grid.status.processed');
      case 'error':
        return t('grid.status.error');
      case 'confirmed_via_portal':
        return t('grid.status.confirmedViaPortal');
      default:
        return t('grid.status.default');
    }
  };

  return (
    <span className={`status-badge ${getStatusClass(value)}`}>
      {getStatusText(value)}
    </span>
  );
};

export default StatusCellRenderer;