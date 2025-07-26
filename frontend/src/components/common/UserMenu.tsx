import React, { useState } from 'react';

interface User {
  name: string;
  role: string;
}

interface UserMenuProps {
  user: User;
}

const UserMenu: React.FC<UserMenuProps> = ({ user }) => {
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
    switch (role) {
      case 'client_user':
        return 'Usuario';
      case 'client_admin':
        return 'Admin Cliente';
      case 'bank_admin':
        return 'Admin Banco';
      default:
        return role;
    }
  };

  const handleLogout = () => {
    // TODO: Implement logout functionality
    console.log('Logout clicked');
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
          <div className="menu-item" onClick={() => console.log('Settings clicked')}>
            Configuración
          </div>
          <div className="menu-item" onClick={() => console.log('Reports clicked')}>
            Reportes
          </div>
          <div className="menu-divider"></div>
          <div className="menu-item logout" onClick={handleLogout}>
            Cerrar Sesión
          </div>
        </div>
      )}
    </div>
  );
};

export default UserMenu;