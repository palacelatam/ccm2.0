import React, { useState } from 'react';
import { AlertSettings as AlertSettingsType } from '../../services/api';
import './SettingsComponents.css';

interface AlertSettingsProps {
  settings: AlertSettingsType;
  onSave: (settings: AlertSettingsType) => void;
  saving: boolean;
}

const AlertSettings: React.FC<AlertSettingsProps> = ({
  settings,
  onSave,
  saving
}) => {
  const [formData, setFormData] = useState<AlertSettingsType>(settings);
  const [hasChanges, setHasChanges] = useState(false);
  const [newEmail, setNewEmail] = useState('');
  const [newPhone, setNewPhone] = useState('');

  const handleChange = (field: string, value: any) => {
    const newData = { ...formData };
    
    if (field.includes('.')) {
      const parts = field.split('.');
      let current = newData as any;
      for (let i = 0; i < parts.length - 1; i++) {
        current = current[parts[i]];
      }
      current[parts[parts.length - 1]] = value;
    } else {
      (newData as any)[field] = value;
    }
    
    setFormData(newData);
    setHasChanges(true);
  };

  const addEmail = (type: 'emailConfirmedTrades' | 'emailDisputedTrades') => {
    if (newEmail && !formData[type].emails.includes(newEmail)) {
      const emails = [...formData[type].emails, newEmail];
      handleChange(`${type}.emails`, emails);
      setNewEmail('');
    }
  };

  const removeEmail = (type: 'emailConfirmedTrades' | 'emailDisputedTrades', email: string) => {
    const emails = formData[type].emails.filter(e => e !== email);
    handleChange(`${type}.emails`, emails);
  };

  const addPhone = (type: 'whatsappConfirmedTrades' | 'whatsappDisputedTrades') => {
    if (newPhone && !formData[type].phones.includes(newPhone)) {
      const phones = [...formData[type].phones, newPhone];
      handleChange(`${type}.phones`, phones);
      setNewPhone('');
    }
  };

  const removePhone = (type: 'whatsappConfirmedTrades' | 'whatsappDisputedTrades', phone: string) => {
    const phones = formData[type].phones.filter(p => p !== phone);
    handleChange(`${type}.phones`, phones);
  };

  const handleSave = () => {
    onSave(formData);
    setHasChanges(false);
  };

  const handleReset = () => {
    setFormData(settings);
    setHasChanges(false);
  };

  return (
    <div className="settings-section">
      <div className="settings-section-header">
        <h2>Alert Settings</h2>
        <p>Configure email and WhatsApp notifications for trade confirmations and disputes</p>
      </div>

      <div className="settings-form">
        {/* Email Confirmed Trades */}
        <div className="form-group">
          <h3>Email Notifications - Confirmed Trades</h3>
          <div className="form-row">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={formData.emailConfirmedTrades.enabled}
                onChange={(e) => handleChange('emailConfirmedTrades.enabled', e.target.checked)}
              />
              <span className="checkmark"></span>
              <div className="label-content">
                <span className="label-title">Enable Email Notifications</span>
                <span className="label-description">
                  Send email notifications when trades are confirmed
                </span>
              </div>
            </label>
          </div>
          
          {formData.emailConfirmedTrades.enabled && (
            <div className="list-input-group">
              <div className="list-input-row">
                <input
                  type="email"
                  value={newEmail}
                  onChange={(e) => setNewEmail(e.target.value)}
                  placeholder="Enter email address"
                  className="text-input"
                />
                <button
                  onClick={() => addEmail('emailConfirmedTrades')}
                  className="btn-small btn-add"
                  disabled={!newEmail}
                >
                  Add Email
                </button>
              </div>
              <div className="email-list">
                {formData.emailConfirmedTrades.emails.map((email, index) => (
                  <div key={index} className="list-item">
                    <span>{email}</span>
                    <button
                      onClick={() => removeEmail('emailConfirmedTrades', email)}
                      className="btn-small btn-remove"
                    >
                      Remove
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Email Disputed Trades */}
        <div className="form-group">
          <h3>Email Notifications - Disputed Trades</h3>
          <div className="form-row">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={formData.emailDisputedTrades.enabled}
                onChange={(e) => handleChange('emailDisputedTrades.enabled', e.target.checked)}
              />
              <span className="checkmark"></span>
              <div className="label-content">
                <span className="label-title">Enable Email Notifications</span>
                <span className="label-description">
                  Send email notifications when trades are disputed
                </span>
              </div>
            </label>
          </div>
          
          {formData.emailDisputedTrades.enabled && (
            <div className="list-input-group">
              <div className="list-input-row">
                <input
                  type="email"
                  value={newEmail}
                  onChange={(e) => setNewEmail(e.target.value)}
                  placeholder="Enter email address"
                  className="text-input"
                />
                <button
                  onClick={() => addEmail('emailDisputedTrades')}
                  className="btn-small btn-add"
                  disabled={!newEmail}
                >
                  Add Email
                </button>
              </div>
              <div className="email-list">
                {formData.emailDisputedTrades.emails.map((email, index) => (
                  <div key={index} className="list-item">
                    <span>{email}</span>
                    <button
                      onClick={() => removeEmail('emailDisputedTrades', email)}
                      className="btn-small btn-remove"
                    >
                      Remove
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* WhatsApp Confirmed Trades */}
        <div className="form-group">
          <h3>WhatsApp Notifications - Confirmed Trades</h3>
          <div className="form-row">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={formData.whatsappConfirmedTrades.enabled}
                onChange={(e) => handleChange('whatsappConfirmedTrades.enabled', e.target.checked)}
              />
              <span className="checkmark"></span>
              <div className="label-content">
                <span className="label-title">Enable WhatsApp Notifications</span>
                <span className="label-description">
                  Send WhatsApp notifications when trades are confirmed
                </span>
              </div>
            </label>
          </div>
          
          {formData.whatsappConfirmedTrades.enabled && (
            <div className="list-input-group">
              <div className="list-input-row">
                <input
                  type="tel"
                  value={newPhone}
                  onChange={(e) => setNewPhone(e.target.value)}
                  placeholder="Enter phone number (e.g., +56912345678)"
                  className="text-input"
                />
                <button
                  onClick={() => addPhone('whatsappConfirmedTrades')}
                  className="btn-small btn-add"
                  disabled={!newPhone}
                >
                  Add Phone
                </button>
              </div>
              <div className="phone-list">
                {formData.whatsappConfirmedTrades.phones.map((phone, index) => (
                  <div key={index} className="list-item">
                    <span>{phone}</span>
                    <button
                      onClick={() => removePhone('whatsappConfirmedTrades', phone)}
                      className="btn-small btn-remove"
                    >
                      Remove
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* WhatsApp Disputed Trades */}
        <div className="form-group">
          <h3>WhatsApp Notifications - Disputed Trades</h3>
          <div className="form-row">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={formData.whatsappDisputedTrades.enabled}
                onChange={(e) => handleChange('whatsappDisputedTrades.enabled', e.target.checked)}
              />
              <span className="checkmark"></span>
              <div className="label-content">
                <span className="label-title">Enable WhatsApp Notifications</span>
                <span className="label-description">
                  Send WhatsApp notifications when trades are disputed
                </span>
              </div>
            </label>
          </div>
          
          {formData.whatsappDisputedTrades.enabled && (
            <div className="list-input-group">
              <div className="list-input-row">
                <input
                  type="tel"
                  value={newPhone}
                  onChange={(e) => setNewPhone(e.target.value)}
                  placeholder="Enter phone number (e.g., +56912345678)"
                  className="text-input"
                />
                <button
                  onClick={() => addPhone('whatsappDisputedTrades')}
                  className="btn-small btn-add"
                  disabled={!newPhone}
                >
                  Add Phone
                </button>
              </div>
              <div className="phone-list">
                {formData.whatsappDisputedTrades.phones.map((phone, index) => (
                  <div key={index} className="list-item">
                    <span>{phone}</span>
                    <button
                      onClick={() => removePhone('whatsappDisputedTrades', phone)}
                      className="btn-small btn-remove"
                    >
                      Remove
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="settings-actions">
        <button
          onClick={handleReset}
          disabled={!hasChanges || saving}
          className="btn-secondary"
        >
          Reset Changes
        </button>
        <button
          onClick={handleSave}
          disabled={!hasChanges || saving}
          className="btn-primary"
        >
          {saving ? 'Saving...' : 'Save Changes'}
        </button>
      </div>
    </div>
  );
};

export default AlertSettings;