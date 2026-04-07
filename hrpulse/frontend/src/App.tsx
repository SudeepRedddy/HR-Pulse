import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/Layout';
import { Dashboard } from './pages/Dashboard';
import { Employees } from './pages/Employees';
import { Analytics } from './pages/Analytics';
import { Recruitment } from './pages/Recruitment';
import { Login } from './pages/Login';
import { Settings } from './pages/Settings';
import { FloatingAria } from './components/chat/FloatingAria';

const AuthGuard = ({ children }: { children: React.ReactNode }) => {
  const token = localStorage.getItem('hrpulse_token');
  if (!token) return <Navigate to="/login" replace />;
  return <>{children}</>;
};

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        
        {/* Protected Routes */}
        <Route path="/" element={<AuthGuard><Layout><Dashboard /><FloatingAria /></Layout></AuthGuard>} />
        <Route path="/analytics" element={<AuthGuard><Layout><Analytics /><FloatingAria /></Layout></AuthGuard>} />
        <Route path="/employees" element={<AuthGuard><Layout><Employees /><FloatingAria /></Layout></AuthGuard>} />
        <Route path="/recruitment" element={<AuthGuard><Layout><Recruitment /><FloatingAria /></Layout></AuthGuard>} />
        <Route path="/settings" element={<AuthGuard><Layout><Settings /><FloatingAria /></Layout></AuthGuard>} />
        
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
