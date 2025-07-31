import React, { createContext, useContext, useState, useEffect } from 'react';

interface User {
  id: string;
  name: string;
  email: string;
  role: 'client_user' | 'client_admin' | 'bank_admin';
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // TODO: Check for existing authentication session
    // For now, just finish loading without setting a user
    setTimeout(() => {
      setLoading(false);
    }, 500);
  }, []);

  const login = async (email: string, password: string) => {
    setLoading(true);
    try {
      console.log('Login attempt:', { email, password });
      
      // Mock user database
      const mockUsers = {
        'admin@xyz.cl': {
          id: '1',
          name: 'Admin Cliente XYZ',
          email: 'admin@xyz.cl',
          role: 'client_admin' as const
        },
        'usuario@xyz.cl': {
          id: '2', 
          name: 'Usuario Cliente XYZ',
          email: 'usuario@xyz.cl',
          role: 'client_user' as const
        },
        'admin@bancoabc.cl': {
          id: '3',
          name: 'Admin Banco ABC',
          email: 'admin@bancoabc.cl',
          role: 'bank_admin' as const
        }
      };

      // Mock login authentication
      setTimeout(() => {
        const user = mockUsers[email as keyof typeof mockUsers];
        
        if (user && password.length > 0) {
          setUser(user);
          setLoading(false);
        } else {
          setLoading(false);
          throw new Error('Invalid credentials. Use one of: admin@xyz.cl, usuario@xyz.cl, admin@bancoabc.cl');
        }
      }, 1500);
    } catch (error) {
      setLoading(false);
      throw error;
    }
  };

  const logout = () => {
    // TODO: Implement Firebase logout
    setUser(null);
  };

  const value = {
    user,
    loading,
    login,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};