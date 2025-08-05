import React, { useState } from 'react';
import { AutomationSettings as AutomationSettingsType } from '../../services/api';
import './SettingsComponents.css';

interface AutomationSettingsProps {
  settings: AutomationSettingsType;
  onSave: (settings: AutomationSettingsType) => void;
  saving: boolean;
}

const AutomationSettings: React.FC<AutomationSettingsProps> = ({
  settings,
  onSave,
  saving
}) => {
  const [formData, setFormData] = useState<AutomationSettingsType>(settings);
  const [hasChanges, setHasChanges] = useState(false);

  const handleChange = (field: string, value: any) => {
    const newData = { ...formData };
    
    if (field.includes('.')) {
      const [parent, child] = field.split('.');
      newData[parent as keyof AutomationSettingsType] = {
        ...(newData[parent as keyof AutomationSettingsType] as any),
        [child]: value
      };
    } else {
      (newData as any)[field] = value;
    }
    
    setFormData(newData);
    setHasChanges(true);
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
        <h2>Automation Settings</h2>
        <p>Configure automatic trade processing and confirmation behaviors</p>
      </div>

      <div className="settings-form">
        {/* Data Sharing */}
        <div className="form-group">
          <div className="form-row">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={formData.dataSharing}
                onChange={(e) => handleChange('dataSharing', e.target.checked)}
              />
              <span className="checkmark"></span>
              <div className="label-content">
                <span className="label-title">Data Sharing</span>
                <span className="label-description">
                  Allow sharing confirmed trade data with banks for reconciliation
                </span>
              </div>
            </label>
          </div>
        </div>

        {/* Auto Confirm Matched Trades */}
        <div className="form-group">
          <h3>Auto-Confirm Matched Trades</h3>
          <div className="form-row">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={formData.autoConfirmMatched.enabled}
                onChange={(e) => handleChange('autoConfirmMatched.enabled', e.target.checked)}
              />
              <span className="checkmark"></span>
              <div className="label-content">
                <span className="label-title">Enable Auto-Confirmation</span>
                <span className="label-description">
                  Automatically confirm trades that match your internal records
                </span>
              </div>
            </label>
          </div>
          
          {formData.autoConfirmMatched.enabled && (
            <div className="form-row">
              <label className="input-label">
                <span className="label-title">Delay Before Confirmation (minutes)</span>
                <input
                  type="number"
                  min="0"
                  max="1440"
                  value={formData.autoConfirmMatched.delayMinutes}
                  onChange={(e) => handleChange('autoConfirmMatched.delayMinutes', parseInt(e.target.value) || 0)}
                  className="number-input"
                />
                <span className="label-description">
                  Wait time before automatically confirming matched trades (0-1440 minutes)
                </span>
              </label>
            </div>
          )}
        </div>

        {/* Auto Carta Instrucción */}
        <div className="form-group">
          <div className="form-row">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={formData.autoCartaInstruccion}
                onChange={(e) => handleChange('autoCartaInstruccion', e.target.checked)}
              />
              <span className="checkmark"></span>
              <div className="label-content">
                <span className="label-title">Auto-Generate Settlement Instructions</span>
                <span className="label-description">
                  Automatically generate carta instrucción for confirmed trades
                </span>
              </div>
            </label>
          </div>
        </div>

        {/* Auto Confirm Disputed Trades */}
        <div className="form-group">
          <h3>Auto-Confirm Disputed Trades</h3>
          <div className="form-row">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={formData.autoConfirmDisputed.enabled}
                onChange={(e) => handleChange('autoConfirmDisputed.enabled', e.target.checked)}
              />
              <span className="checkmark"></span>
              <div className="label-content">
                <span className="label-title">Enable Auto-Confirmation for Disputes</span>
                <span className="label-description">
                  Automatically confirm disputed trades after review period
                </span>
              </div>
            </label>
          </div>
          
          {formData.autoConfirmDisputed.enabled && (
            <div className="form-row">
              <label className="input-label">
                <span className="label-title">Delay Before Confirmation (minutes)</span>
                <input
                  type="number"
                  min="0"
                  max="10080"
                  value={formData.autoConfirmDisputed.delayMinutes}
                  onChange={(e) => handleChange('autoConfirmDisputed.delayMinutes', parseInt(e.target.value) || 0)}
                  className="number-input"
                />
                <span className="label-description">
                  Wait time before automatically confirming disputed trades (0-10080 minutes = 1 week)
                </span>
              </label>
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

export default AutomationSettings;