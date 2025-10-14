import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import LanguageSwitcher from './LanguageSwitcher';
import UserMenu from './UserMenu';
import './TopBanner.css';

const TopBanner: React.FC = () => {
  const { t } = useTranslation();
  const location = useLocation();
  const { user } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <div className="top-banner">
      <div className="banner-left">
        <div className="logo-container">
          <img src="/palace.jpg" alt="Palace Technology" className="palace-logo" />
        </div>
      </div>

      <div className="banner-right">
        <div className="app-title">
          <h2>{t('navigation.title')}</h2>
        </div>
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
              {/* Dashboard - Available to client users only */}
              {(user?.role === 'client_user' || user?.role === 'client_admin') && (
                <Link 
                  to="/" 
                  className={`menu-item ${location.pathname === '/' ? 'active' : ''}`}
                  onClick={() => setMenuOpen(false)}
                >
                  {t('navigation.dashboard')}
                </Link>
              )}
              
              {/* Client Admin Panel - Only for client_admin */}
              {user?.role === 'client_admin' && (
                <>
                  <Link
                    to="/admin"
                    className={`menu-item ${location.pathname === '/admin' ? 'active' : ''}`}
                    onClick={() => setMenuOpen(false)}
                  >
                    {t('navigation.clientAdmin')}
                  </Link>
                  <Link
                    to="/reports"
                    className={`menu-item ${location.pathname === '/reports' ? 'active' : ''}`}
                    onClick={() => setMenuOpen(false)}
                  >
                    {t('navigation.reports')}
                  </Link>
                </>
              )}
              
              {/* Bank Admin Panel - Only for bank_admin */}
              {user?.role === 'bank_admin' && (
                <>
                  <Link 
                    to="/bank" 
                    className={`menu-item ${location.pathname === '/bank' ? 'active' : ''}`}
                    onClick={() => setMenuOpen(false)}
                  >
                    {t('navigation.bankAdmin')}
                  </Link>
                  <Link 
                    to="/fx-analytics" 
                    className={`menu-item ${location.pathname === '/fx-analytics' ? 'active' : ''}`}
                    onClick={() => setMenuOpen(false)}
                  >
                    {t('navigation.fxAnalytics')}
                  </Link>
                </>
              )}
            </div>
          )}
        </div>
        {user && <UserMenu user={user} />}
      </div>
    </div>
  );
};

export default TopBanner;