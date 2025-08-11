import React, { createContext, useContext, useState, useEffect } from 'react';
import { signInWithEmailAndPassword, signOut, onAuthStateChanged, User as FirebaseUser } from 'firebase/auth';
import { auth } from '../../config/firebase';
import { userService, UserProfile } from '../../services/api';

interface OrganizationInfo {
  id: string;
  name: string;
  type: 'client' | 'bank';
}

interface User {
  id: string;
  name: string;
  email: string;
  role: 'client_user' | 'client_admin' | 'bank_admin';
  profile?: UserProfile; // Add backend profile data
  permissions?: string[]; // Add backend permissions
  organization?: OrganizationInfo; // Add organization info
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
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      if (firebaseUser) {
        try {
          // Get user profile from backend
          const profileResponse = await userService.getMyProfile();
          const profile = profileResponse.data;
          
          // Map Firebase user with backend profile data
          const mappedUser = mapFirebaseUserToUser(firebaseUser, profile);
          setUser(mappedUser);
        } catch (error) {
          console.error('Failed to load user profile from backend:', error);
          // Fallback to Firebase-only user
          const mappedUser = mapFirebaseUserToUser(firebaseUser);
          setUser(mappedUser);
        }
      } else {
        setUser(null);
      }
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  // Helper function to map Firebase user to our User interface
  const mapFirebaseUserToUser = (firebaseUser: FirebaseUser, profile?: UserProfile): User => {
    // Determine role based on backend profile or email domain fallback
    let role: 'client_user' | 'client_admin' | 'bank_admin';
    
    if (profile?.organization?.type === 'bank') {
      role = 'bank_admin';
    } else if (profile?.organization?.type === 'client' && profile?.primaryRole === 'client_admin') {
      role = 'client_admin';
    } else if (firebaseUser.email?.includes('@bancoabc.cl')) {
      role = 'bank_admin';
    } else if (firebaseUser.email === 'admin@xyz.cl') {
      role = 'client_admin';
    } else {
      role = 'client_user';
    }

    // Extract organization info from profile or create fallback
    let organization: OrganizationInfo | undefined;
    if (profile?.organization) {
      organization = {
        id: profile.organization.id,
        name: profile.organization.name,
        type: profile.organization.type as 'client' | 'bank'
      };
    } else {
      // Fallback organization info based on user ID for development
      organization = {
        id: firebaseUser.uid, // Use user UID as organization ID
        name: firebaseUser.email?.split('@')[0] || 'Unknown Organization',
        type: role === 'bank_admin' ? 'bank' : 'client'
      };
    }

    return {
      id: firebaseUser.uid,
      name: profile?.fullName || firebaseUser.displayName || firebaseUser.email?.split('@')[0] || 'User',
      email: firebaseUser.email || '',
      role,
      profile,
      organization
    };
  };

  const login = async (email: string, password: string) => {
    setLoading(true);
    try {
      // Use Firebase Auth to sign in
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      
      // User will be set automatically by the onAuthStateChanged listener
      
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