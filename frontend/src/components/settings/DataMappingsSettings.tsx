import React from 'react';
import './SettingsComponents.css';

interface DataMappingsSettingsProps {
  clientId: string;
}

const DataMappingsSettings: React.FC<DataMappingsSettingsProps> = ({ clientId }) => {
  return (
    <div className="settings-section">
      <div className="settings-section-header">
        <h2>Data Mappings</h2>
        <p>Configure how to map and transform data from different file formats</p>
      </div>

      <div className="settings-form">
        <div className="empty-state">
          <p>Data mappings configuration will be implemented in a future update.</p>
          <p>This feature will allow you to configure how CSV and Excel files are processed and mapped to the system fields.</p>
        </div>
      </div>
    </div>
  );
};

export default DataMappingsSettings;