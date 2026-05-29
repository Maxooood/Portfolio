import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';

import { Layout } from './components/Layout';
import { ProtectedRoute } from './components/ProtectedRoute';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { EquipmentPage } from './pages/Equipment';
import { PprSchedulePage } from './pages/PprSchedule';
import { Requests } from './pages/Requests';
import { RequestDetailPage } from './pages/RequestDetail';
import { Analytics } from './pages/Analytics';
import { Admin } from './pages/Admin';
import { useAuthStore } from './store/auth';

function App() {
  const { isAuthenticated } = useAuthStore();

  return (
    <BrowserRouter>
      <Toaster position="top-right" />
      <Routes>
        <Route
          path="/login"
          element={isAuthenticated ? <Navigate to="/" replace /> : <Login />}
        />
        <Route
          path="/*"
          element={
            <ProtectedRoute>
              <Layout>
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/equipment" element={<EquipmentPage />} />
                  <Route
                    path="/ppr"
                    element={
                      <ProtectedRoute roles={['admin', 'manager', 'dispatcher', 'ppr_engineer']}>
                        <PprSchedulePage />
                      </ProtectedRoute>
                    }
                  />
                  <Route path="/requests" element={<Requests />} />
                  <Route path="/requests/:id" element={<RequestDetailPage />} />
                  <Route
                    path="/analytics"
                    element={
                      <ProtectedRoute roles={['admin', 'manager', 'dispatcher']}>
                        <Analytics />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/admin"
                    element={
                      <ProtectedRoute roles={['admin', 'manager']}>
                        <Admin />
                      </ProtectedRoute>
                    }
                  />
                  <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
              </Layout>
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
