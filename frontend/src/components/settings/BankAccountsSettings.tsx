import React, { useState, useEffect } from 'react';
import { clientService, BankAccount } from '../../services/api';
import './SettingsComponents.css';

interface BankAccountsSettingsProps {
  clientId: string;
}

const BankAccountsSettings: React.FC<BankAccountsSettingsProps> = ({ clientId }) => {
  const [accounts, setAccounts] = useState<BankAccount[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadAccounts();
  }, [clientId]);

  const loadAccounts = async () => {
    try {
      setLoading(true);
      const response = await clientService.getBankAccounts(clientId);
      setAccounts(response.data);
      setError(null);
    } catch (err: any) {
      console.error('Failed to load bank accounts:', err);
      setError('Failed to load bank accounts');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="settings-section">
        <div className="loading">Loading bank accounts...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="settings-section">
        <div className="error">
          <p>{error}</p>
          <button onClick={loadAccounts}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="settings-section">
      <div className="settings-section-header">
        <h2>Bank Accounts</h2>
        <p>Manage your organization's bank accounts for settlement processing</p>
      </div>

      <div className="settings-form">
        {accounts.length === 0 ? (
          <div className="empty-state">
            <p>No bank accounts configured yet.</p>
            <button className="btn-primary">Add Bank Account</button>
          </div>
        ) : (
          <div className="accounts-list">
            {accounts.map((account) => (
              <div key={account.id} className="account-card">
                <div className="account-header">
                  <h3>{account.accountName}</h3>
                  <div className="account-status">
                    <span className={`status-badge ${account.active ? 'active' : 'inactive'}`}>
                      {account.active ? 'Active' : 'Inactive'}
                    </span>
                    {account.isDefault && (
                      <span className="status-badge default">Default</span>
                    )}
                  </div>
                </div>
                <div className="account-details">
                  <div className="detail-row">
                    <span className="detail-label">Bank:</span>
                    <span className="detail-value">{account.bankName}</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Currency:</span>
                    <span className="detail-value">{account.accountCurrency}</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Account Number:</span>
                    <span className="detail-value">{account.accountNumber}</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">SWIFT Code:</span>
                    <span className="detail-value">{account.swiftCode}</span>
                  </div>
                </div>
                <div className="account-actions">
                  <button className="btn-small btn-secondary">Edit</button>
                  <button className="btn-small btn-remove">Delete</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="settings-actions">
        <button className="btn-primary">Add New Account</button>
      </div>
    </div>
  );
};

export default BankAccountsSettings;