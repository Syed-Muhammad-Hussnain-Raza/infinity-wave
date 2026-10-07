import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import AppLayout from './components/layout/AppLayout';
import Login from './pages/auth/Login';
import CreateTranscript from './pages/admin/CreateTranscript';
import AdminDashboard from './pages/admin/AdminDashboard';
import TeamDirectory from './pages/admin/TeamDirectory';
import ProjectList from './pages/projects/ProjectList';
import ProjectDetail from './pages/projects/ProjectDetail';
import MyTasks from './pages/agent/MyTasks';

function ProtectedRoute({ children, allowedRoles }: { children: React.ReactNode, allowedRoles?: string[] }) {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  if (allowedRoles && !allowedRoles.includes(user.role)) return <Navigate to={`/${user.role.toLowerCase()}`} replace />;
  return <>{children}</>;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="/login" element={<Login />} />
      
      <Route element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
        <Route path="/admin" element={<ProtectedRoute allowedRoles={['ADMIN']}><AdminDashboard /></ProtectedRoute>} />
        <Route path="/admin/transcript" element={<ProtectedRoute allowedRoles={['ADMIN']}><CreateTranscript /></ProtectedRoute>} />
        
        {/* Manager dashboard is just the project list scoped to them via backend API */}
        <Route path="/manager" element={<ProtectedRoute allowedRoles={['MANAGER']}><ProjectList title="Manager Dashboard" /></ProtectedRoute>} />
        
        <Route path="/my-tasks" element={<ProtectedRoute allowedRoles={['AGENT']}><MyTasks /></ProtectedRoute>} />
        
        <Route path="/team" element={<ProtectedRoute allowedRoles={['ADMIN']}><TeamDirectory /></ProtectedRoute>} />
        <Route path="/projects" element={<ProtectedRoute allowedRoles={['ADMIN', 'MANAGER']}><ProjectList /></ProtectedRoute>} />
        <Route path="/projects/:id" element={<ProtectedRoute allowedRoles={['ADMIN', 'MANAGER']}><ProjectDetail /></ProtectedRoute>} />
      </Route>
    </Routes>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  );
}
