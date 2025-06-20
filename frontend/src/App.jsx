import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import LoginPage from './components/LoginPage';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import CustomersPage from './components/CustomersPage';
import OrdersPage from './components/OrdersPage';
import DeliveriesPage from './components/DeliveriesPage';
import './App.css';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-orange-600"></div>
      </div>
    );
  }
  
  return isAuthenticated ? children : <Navigate to="/login" />;
};

// Main Layout Component
const Layout = ({ children }) => {
  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <main className="flex-1 overflow-y-auto lg:ml-0">
        {children}
      </main>
    </div>
  );
};

// App Routes Component
const AppRoutes = () => {
  const { isAuthenticated } = useAuth();

  if (isAuthenticated) {
    return (
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/customers" element={<CustomersPage />} />
          <Route path="/orders" element={<OrdersPage />} />
          <Route path="/deliveries" element={<DeliveriesPage />} />
          <Route path="/payments" element={<div className="p-6"><h1 className="text-3xl font-bold">Payments</h1><p className="text-gray-600 mt-2">Payments management coming soon...</p></div>} />
          <Route path="/reports" element={<div className="p-6"><h1 className="text-3xl font-bold">Reports</h1><p className="text-gray-600 mt-2">Reports and analytics coming soon...</p></div>} />
          <Route path="/settings" element={<div className="p-6"><h1 className="text-3xl font-bold">Settings</h1><p className="text-gray-600 mt-2">Settings panel coming soon...</p></div>} />
          <Route path="/login" element={<Navigate to="/" />} />
        </Routes>
      </Layout>
    );
  }

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="*" element={<Navigate to="/login" />} />
    </Routes>
  );
};

// Main App Component
function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <AppRoutes />
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;

