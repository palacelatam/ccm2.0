import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../auth/AuthContext';

interface User {
  name: string;
  role: string;
}

interface UserMenuProps {
  user: User;
}

const UserMenu: React.FC<UserMenuProps> = ({ user }) => {
  const { t } = useTranslation();
  const { logout } = useAuth();
  const [isOpen, setIsOpen] = useState(false);

  const getUserInitials = (name: string) => {
    return name
      .split(' ')
      .map(word => word.charAt(0))
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const getRoleDisplay = (role: string) => {
    return t(`userMenu.roles.${role}`) || role;
  };

  const handleLogout = () => {
    logout();
    setIsOpen(false);
  };

  return (
    <div className="user-menu">
      <div 
        className="user-menu-trigger"
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="user-avatar">
          {getUserInitials(user.name)}
        </div>
        <div className="user-info">
          <div className="user-name">{user.name}</div>
          <div className="user-role">{getRoleDisplay(user.role)}</div>
        </div>
      </div>
      
      {isOpen && (
        <div className="user-menu-dropdown">
          <div className="menu-item logout" onClick={handleLogout}>
            {t('userMenu.logout')}
          </div>
        </div>
      )}
    </div>
  );
};

export default UserMenu;