import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useLocation } from 'react-router-dom';
import LanguageSwitcher from './LanguageSwitcher';
import UserMenu from './UserMenu';
import './TopBanner.css';

const TopBanner: React.FC = () => {
  const { t } = useTranslation();
  const location = useLocation();
  const [user] = useState({ name: 'Usuario Demo', role: 'client_admin' }); // Mock user
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <div className="top-banner">
      <div className="banner-left">
        <div className="logo-container">
          <img src="/palace.jpg" alt="Palace Technology" className="palace-logo" />
        </div>
        <div className="app-title">
          <h2>{t('navigation.title')}</h2>
        </div>
      </div>
      
      <div className="banner-right">
        <LanguageSwitcher />
        <div className="navigation-menu">
          <button 
            className="menu-toggle"
            onClick={() => setMenuOpen(!menuOpen)}
          >
            ☰
          </button>
          {menuOpen && (
            <div className="menu-dropdown">
              <Link 
                to="/" 
                className={`menu-item ${location.pathname === '/' ? 'active' : ''}`}
                onClick={() => setMenuOpen(false)}
              >
                Dashboard
              </Link>
              <Link 
                to="/admin" 
                className={`menu-item ${location.pathname === '/admin' ? 'active' : ''}`}
                onClick={() => setMenuOpen(false)}
              >
                Administración
              </Link>
            </div>
          )}
        </div>
        <UserMenu user={user} />
      </div>
    </div>
  );
};

export default TopBanner;