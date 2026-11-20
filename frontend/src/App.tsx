import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import LoginPage from './pages/Login';
import RegisterPage from './pages/Register';
import DashboardPage from './pages/Dashboard';
import SubmitComplaintPage from './pages/SubmitComplaint';
import ComplaintDetailPage from './pages/ComplaintDetail';
import TrackComplaintsPage from './pages/TrackComplaints';
import CivicMapPage from './pages/CivicMap';
import AdminDashboardPage from './pages/AdminDashboard';
import DepartmentsPage from './pages/Departments';
import WardMapPage from './pages/WardMap';
import { useAuthStore } from './store/auth';

function PrivateRoute({ children }: { children: JSX.Element }) {
  const accessToken = useAuthStore((state) => state.accessToken);
  return accessToken ? <Layout>{children}</Layout> : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        {/* Protected App Routes */}
        <Route
          path="/dashboard"
          element={
            <PrivateRoute>
              <DashboardPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/submit"
          element={
            <PrivateRoute>
              <SubmitComplaintPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/complaints"
          element={
            <PrivateRoute>
              <TrackComplaintsPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/complaints/:id"
          element={
            <PrivateRoute>
              <ComplaintDetailPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/map"
          element={
            <PrivateRoute>
              <CivicMapPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/admin"
          element={
            <PrivateRoute>
              <AdminDashboardPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/departments"
          element={
            <PrivateRoute>
              <DepartmentsPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/ward-map"
          element={
            <PrivateRoute>
              <WardMapPage />
            </PrivateRoute>
          }
        />

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Router>
  );
}
