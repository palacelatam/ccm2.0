import React from 'react';

const AdminDashboard: React.FC = () => {
  return (
    <div className="dashboard-container">
      <div className="admin-dashboard">
        <h2>Panel de Administración</h2>
        <div className="dashboard-sections">
          <div className="section-card">
            <h3>Configuración de Alertas</h3>
            <p>Configurar alertas por email y WhatsApp</p>
            <button className="section-button">Configurar</button>
          </div>
          <div className="section-card">
            <h3>Reglas de Liquidación</h3>
            <p>Gestionar instrucciones de liquidación</p>
            <button className="section-button">Gestionar Reglas</button>
          </div>
          <div className="section-card">
            <h3>Mapeo de Datos</h3>
            <p>Configurar mapeo de archivos CSV/Excel</p>
            <button className="section-button">Configurar Mapeo</button>
          </div>
          <div className="section-card">
            <h3>Compartir Datos</h3>
            <p>Configurar políticas de compartir datos</p>
            <button className="section-button">Configurar</button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;