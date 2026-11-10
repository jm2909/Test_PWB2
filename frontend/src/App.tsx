import { Navigate, Route, Routes } from 'react-router-dom';
import RequireAuth from './components/auth/RequireAuth';
import Layout from './components/layout/Layout';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import OnboardingPage from './pages/OnboardingPage';
import DashboardPage from './pages/DashboardPage';
import SyncStatusPage from './pages/SyncStatusPage';
import DevicesPage from './pages/DevicesPage';
import GoalsPage from './pages/GoalsPage';
import TrendsPage from './pages/TrendsPage';
import InsightsPage from './pages/InsightsPage';

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route element={<RequireAuth />}>
        <Route path="/onboarding" element={<OnboardingPage />} />
        <Route element={<Layout />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/devices" element={<DevicesPage />} />
          <Route path="/devices/sync" element={<SyncStatusPage />} />
          <Route path="/trends" element={<TrendsPage />} />
          <Route path="/insights" element={<InsightsPage />} />
          <Route path="/goals" element={<GoalsPage />} />
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
