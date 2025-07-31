import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './components/auth/AuthContext';
import Layout from './components/common/Layout';
import ClientDashboard from './pages/client/ClientDashboard';
import BankDashboard from './pages/bank/BankDashboard';
import AdminDashboard from './pages/admin/AdminDashboard';
import Login from './pages/auth/Login';
import './styles/App.css';

const ProtectedRoute: React.FC<{ 
  children: React.ReactNode;
  allowedRoles?: string[];
}> = ({ children, allowedRoles }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return <div>Loading...</div>;
  }
  
  if (!user) {
    return <Navigate to="/login" />;
  }
  
  if (allowedRoles && !allowedRoles.includes(user.role)) {
    // Redirect to appropriate default page based on user role
    if (user.role === 'bank_admin') {
      return <Navigate to="/bank" />;
    } else {
      return <Navigate to="/" />;
    }
  }
  
  return <>{children}</>;
};

function AppRoutes() {
  const { user } = useAuth();
  
  const getDefaultRoute = () => {
    if (!user) return "/login";
    if (user.role === 'bank_admin') return "/bank";
    return "/";
  };
  
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/login" element={user ? <Navigate to={getDefaultRoute()} /> : <Login />} />
          <Route path="/" element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }>
            <Route index element={
              <ProtectedRoute allowedRoles={['client_user', 'client_admin']}>
                <ClientDashboard />
              </ProtectedRoute>
            } />
            <Route path="client" element={
              <ProtectedRoute allowedRoles={['client_user', 'client_admin']}>
                <ClientDashboard />
              </ProtectedRoute>
            } />
            <Route path="bank" element={
              <ProtectedRoute allowedRoles={['bank_admin']}>
                <BankDashboard />
              </ProtectedRoute>
            } />
            <Route path="admin" element={
              <ProtectedRoute allowedRoles={['client_admin']}>
                <AdminDashboard />
              </ProtectedRoute>
            } />
          </Route>
        </Routes>
      </div>
    </Router>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  );
}

export default App;