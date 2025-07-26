import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './components/auth/AuthContext';
import Layout from './components/common/Layout';
import ClientDashboard from './pages/client/ClientDashboard';
import BankDashboard from './pages/bank/BankDashboard';
import AdminDashboard from './pages/admin/AdminDashboard';
import Login from './pages/auth/Login';
import './styles/App.css';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/" element={<Layout />}>
              <Route index element={<ClientDashboard />} />
              <Route path="client" element={<ClientDashboard />} />
              <Route path="bank" element={<BankDashboard />} />
              <Route path="admin" element={<AdminDashboard />} />
            </Route>
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;