import React, { createContext, useContext, useState, useEffect } from 'react';
import { signInWithEmailAndPassword, signOut, onAuthStateChanged, User as FirebaseUser } from 'firebase/auth';
import { auth } from '../../config/firebase';

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
    // Listen for authentication state changes
    const unsubscribe = onAuthStateChanged(auth, (firebaseUser) => {
      if (firebaseUser) {
        // Map Firebase user to our User interface
        const mappedUser = mapFirebaseUserToUser(firebaseUser);
        setUser(mappedUser);
      } else {
        setUser(null);
      }
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  // Helper function to map Firebase user to our User interface
  const mapFirebaseUserToUser = (firebaseUser: FirebaseUser): User => {
    // Determine role based on email domain
    let role: 'client_user' | 'client_admin' | 'bank_admin';
    
    if (firebaseUser.email?.includes('@bancoabc.cl')) {
      role = 'bank_admin';
    } else if (firebaseUser.email === 'admin@xyz.cl') {
      role = 'client_admin';
    } else {
      role = 'client_user';
    }

    return {
      id: firebaseUser.uid,
      name: firebaseUser.displayName || firebaseUser.email?.split('@')[0] || 'User',
      email: firebaseUser.email || '',
      role
    };
  };

  const login = async (email: string, password: string) => {
    setLoading(true);
    try {
      console.log('Firebase login attempt:', { email });
      
      // Use Firebase Auth to sign in
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      
      // User will be set automatically by the onAuthStateChanged listener
      console.log('Login successful:', userCredential.user.email);
      
    } catch (error: any) {
      setLoading(false);
      console.error('Login error:', error);
      
      // Provide user-friendly error messages
      if (error.code === 'auth/user-not-found' || error.code === 'auth/wrong-password') {
        throw new Error('Invalid email or password');
      } else if (error.code === 'auth/invalid-credential') {
        throw new Error('Invalid credentials');
      } else {
        throw new Error('Login failed. Please try again.');
      }
    }
  };

  const logout = async () => {
    try {
      await signOut(auth);
      // User will be set to null automatically by the onAuthStateChanged listener
    } catch (error) {
      console.error('Logout error:', error);
    }
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