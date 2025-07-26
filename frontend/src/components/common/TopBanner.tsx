import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import LanguageSwitcher from './LanguageSwitcher';
import UserMenu from './UserMenu';
import './TopBanner.css';

const TopBanner: React.FC = () => {
  const { t } = useTranslation();
  const [user] = useState({ name: 'Usuario Demo', role: 'client_admin' }); // Mock user

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
        <UserMenu user={user} />
      </div>
    </div>
  );
};

export default TopBanner;