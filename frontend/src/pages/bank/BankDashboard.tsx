import React from 'react';

const BankDashboard: React.FC = () => {
  return (
    <div className="dashboard-container">
      <div className="bank-dashboard">
        <h2>Panel de Administración Bancaria</h2>
        <div className="dashboard-sections">
          <div className="section-card">
            <h3>Gestión de Plantillas</h3>
            <p>Administrar plantillas de Carta de Instrucción</p>
            <button className="section-button">Gestionar Plantillas</button>
          </div>
          <div className="section-card">
            <h3>Segmentos de Clientes</h3>
            <p>Asignar clientes a diferentes segmentos</p>
            <button className="section-button">Gestionar Segmentos</button>
          </div>
          <div className="section-card">
            <h3>Reportes</h3>
            <p>Ver resúmenes y datos de transacciones</p>
            <button className="section-button">Ver Reportes</button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BankDashboard;