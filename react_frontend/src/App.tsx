import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import ReportPage from './pages/ReportPage';
import UsersPage from './pages/UsersPage';
import GroupsPage from './pages/GroupsPage';
import AdminPage from './pages/AdminPage';
import IncidentDetailPage from './pages/IncidentDetailPage';
import AuditDashboard from './pages/AuditDashboard';
import AuditLogViewer from './pages/AuditLogViewer'; // Import the new page
import { ProtectedRoute } from './context/AuthContext';

import GoogleCallbackPage from './pages/GoogleCallbackPage';

/**
 * Componente principal de la aplicación React.
 *
 * Este componente configura el enrutamiento de la aplicación utilizando React Router.
 * Define las rutas principales de la aplicación, incluyendo rutas protegidas que requieren autenticación.
 *
 * @returns {JSX.Element} El componente raíz de la aplicación envuelto en el Router.
 */
function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/auth/google/callback" element={<GoogleCallbackPage />} />
        <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="report" element={<ReportPage />} />
          <Route path="users" element={<UsersPage />} />
          <Route path="groups" element={<GroupsPage />} />
          <Route path="admin" element={<AdminPage />} />
          <Route path="audit" element={<AuditDashboard />} />
          <Route path="audit-logs" element={<AuditLogViewer />} /> {/* Add the new route */}
          <Route path="incident/:id" element={<IncidentDetailPage />} />
        </Route>
      </Routes>
    </Router>
  )
}

export default App
