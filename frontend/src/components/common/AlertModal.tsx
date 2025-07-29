import React from 'react';
import './AlertModal.css';

interface AlertModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  message: string;
  type?: 'info' | 'warning' | 'error' | 'success';
}

const AlertModal: React.FC<AlertModalProps> = ({ 
  isOpen, 
  onClose, 
  title, 
  message, 
  type = 'info' 
}) => {
  if (!isOpen) return null;

  const getIcon = () => {
    switch (type) {
      case 'warning':
        return '⚠️';
      case 'error':
        return '❌';
      case 'success':
        return '✅';
      default:
        return 'ℹ️';
    }
  };

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div className="alert-modal-backdrop" onClick={handleBackdropClick}>
      <div className={`alert-modal alert-modal-${type}`}>
        <div className="alert-modal-header">
          <span className="alert-modal-icon">{getIcon()}</span>
          <h3 className="alert-modal-title">{title}</h3>
          <button className="alert-modal-close" onClick={onClose}>
            ×
          </button>
        </div>
        <div className="alert-modal-content">
          <p>{message}</p>
        </div>
        <div className="alert-modal-actions">
          <button className="alert-modal-button primary" onClick={onClose}>
            OK
          </button>
        </div>
      </div>
    </div>
  );
};

export default AlertModal;