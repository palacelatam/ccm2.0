import React, { useState } from 'react';
import { PreferencesSettings as PreferencesSettingsType } from '../../services/api';
import './SettingsComponents.css';

interface PreferencesSettingsProps {
  settings: PreferencesSettingsType;
  onSave: (settings: PreferencesSettingsType) => void;
  saving: boolean;
}

const PreferencesSettings: React.FC<PreferencesSettingsProps> = ({
  settings,
  onSave,
  saving
}) => {
  const [formData, setFormData] = useState<PreferencesSettingsType>(settings);
  const [hasChanges, setHasChanges] = useState(false);

  const handleChange = (field: keyof PreferencesSettingsType, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
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
        <h2>Preferences Settings</h2>
        <p>Configure your system preferences and display options</p>
      </div>

      <div className="settings-form">
        {/* Language */}
        <div className="form-group">
          <div className="form-row">
            <label className="input-label">
              <span className="label-title">Language</span>
              <select
                value={formData.language}
                onChange={(e) => handleChange('language', e.target.value)}
                className="select-input"
              >
                <option value="es">Español</option>
                <option value="en">English</option>
                <option value="pt">Português</option>
              </select>
              <span className="label-description">
                Default language for the application interface
              </span>
            </label>
          </div>
        </div>

        {/* Timezone */}
        <div className="form-group">
          <div className="form-row">
            <label className="input-label">
              <span className="label-title">Timezone</span>
              <select
                value={formData.timezone}
                onChange={(e) => handleChange('timezone', e.target.value)}
                className="select-input"
              >
                <option value="America/Santiago">Santiago (America/Santiago)</option>
                <option value="America/New_York">New York (America/New_York)</option>
                <option value="America/Los_Angeles">Los Angeles (America/Los_Angeles)</option>
                <option value="Europe/London">London (Europe/London)</option>
                <option value="Europe/Madrid">Madrid (Europe/Madrid)</option>
                <option value="America/Sao_Paulo">São Paulo (America/Sao_Paulo)</option>
              </select>
              <span className="label-description">
                Timezone used for displaying dates and times
              </span>
            </label>
          </div>
        </div>

        {/* Date Format */}
        <div className="form-group">
          <div className="form-row">
            <label className="input-label">
              <span className="label-title">Date Format</span>
              <select
                value={formData.dateFormat}
                onChange={(e) => handleChange('dateFormat', e.target.value)}
                className="select-input"
              >
                <option value="DD/MM/YYYY">DD/MM/YYYY (31/12/2023)</option>
                <option value="MM/DD/YYYY">MM/DD/YYYY (12/31/2023)</option>
                <option value="YYYY-MM-DD">YYYY-MM-DD (2023-12-31)</option>
                <option value="DD-MM-YYYY">DD-MM-YYYY (31-12-2023)</option>
              </select>
              <span className="label-description">
                Format used for displaying dates throughout the application
              </span>
            </label>
          </div>
        </div>

        {/* Number Format */}
        <div className="form-group">
          <div className="form-row">
            <label className="input-label">
              <span className="label-title">Number Format</span>
              <select
                value={formData.numberFormat}
                onChange={(e) => handleChange('numberFormat', e.target.value)}
                className="select-input"
              >
                <option value="1.234,56">1.234,56 (European)</option>
                <option value="1,234.56">1,234.56 (US/UK)</option>
                <option value="1 234,56">1 234,56 (French)</option>
                <option value="1'234.56">1'234.56 (Swiss)</option>
              </select>
              <span className="label-description">
                Format used for displaying numbers and currency amounts
              </span>
            </label>
          </div>
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

export default PreferencesSettings;