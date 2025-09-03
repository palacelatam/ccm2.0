import React, { useState, useEffect } from 'react';
import { clientService, SettlementRule } from '../../services/api';
import './SettingsComponents.css';

interface SettlementRulesSettingsProps {
  clientId: string;
}

const SettlementRulesSettings: React.FC<SettlementRulesSettingsProps> = ({ clientId }) => {
  const [rules, setRules] = useState<SettlementRule[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadRules();
  }, [clientId]);

  const loadRules = async () => {
    try {
      setLoading(true);
      const response = await clientService.getSettlementRules(clientId);
      setRules(response.data);
      setError(null);
    } catch (err: any) {
      console.error('Failed to load settlement rules:', err);
      setError('Failed to load settlement rules');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="settings-section">
        <div className="loading">Loading settlement rules...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="settings-section">
        <div className="error">
          <p>{error}</p>
          <button onClick={loadRules}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="settings-section">
      <div className="settings-section-header">
        <h2>Settlement Rules</h2>
        <p>Configure automatic settlement rules for different trade types and counterparties</p>
      </div>

      <div className="settings-form">
        {rules.length === 0 ? (
          <div className="empty-state">
            <p>No settlement rules configured yet.</p>
            <button className="btn-primary">Add Settlement Rule</button>
          </div>
        ) : (
          <div className="rules-list">
            {rules.map((rule) => (
              <div key={rule.id} className="rule-card">
                <div className="rule-header">
                  <h3>{rule.name}</h3>
                  <div className="rule-priority">
                    <span className="priority-badge">Priority {rule.priority}</span>
                    <span className={`status-badge ${rule.active ? 'active' : 'inactive'}`}>
                      {rule.active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                </div>
                <div className="rule-details">
                  <div className="detail-row">
                    <span className="detail-label">Counterparty:</span>
                    <span className="detail-value">{rule.counterparty}</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Product:</span>
                    <span className="detail-value">{rule.product}</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Cargar:</span>
                    <span className="detail-value">{rule.cargarCurrency} - {rule.cargarBankName} ({rule.cargarAccountNumber})</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Abonar:</span>
                    <span className="detail-value">{rule.abonarCurrency} - {rule.abonarBankName} ({rule.abonarAccountNumber})</span>
                  </div>
                  {rule.centralBankTradeCode && (
                    <div className="detail-row">
                      <span className="detail-label">Central Bank Code:</span>
                      <span className="detail-value">{rule.centralBankTradeCode}</span>
                    </div>
                  )}
                </div>
                <div className="rule-actions">
                  <button className="btn-small btn-secondary">Edit</button>
                  <button className="btn-small btn-remove">Delete</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="settings-actions">
        <button className="btn-primary">Add New Rule</button>
      </div>
    </div>
  );
};

export default SettlementRulesSettings;