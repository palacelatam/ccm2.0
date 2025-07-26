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
    // For now, simulate loading and set a mock user
    setTimeout(() => {
      setUser({
        id: '1',
        name: 'Usuario Demo',
        email: 'demo@palace.cl',
        role: 'client_admin'
      });
      setLoading(false);
    }, 1000);
  }, []);

  const login = async (email: string, password: string) => {
    setLoading(true);
    try {
      // TODO: Implement Firebase authentication
      console.log('Login attempt:', { email, password });
      
      // Mock login success
      setTimeout(() => {
        setUser({
          id: '1',
          name: 'Usuario Demo',
          email: email,
          role: 'client_admin'
        });
        setLoading(false);
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