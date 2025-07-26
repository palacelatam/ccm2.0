import React from 'react';
import { Outlet } from 'react-router-dom';
import TopBanner from './TopBanner';

const Layout: React.FC = () => {
  return (
    <div className="layout-container">
      <TopBanner />
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;