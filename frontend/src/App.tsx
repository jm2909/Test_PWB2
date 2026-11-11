import { Navigate, Route, Routes } from 'react-router-dom';
import { Layout } from './components/Layout';
import { NotFoundRedirect } from './components/NotFoundRedirect';
import { RequireAuth } from './components/auth/RequireAuth';
import { AccountAccessPage } from './pages/AccountAccessPage';
import { DashboardPage } from './pages/DashboardPage';
import { ConnectionsPage } from './pages/ConnectionsPage';
import { TrendsPage } from './pages/TrendsPage';
import { ConsentPage } from './pages/ConsentPage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { AlertsPage } from './pages/AlertsPage';
import { GoalsPage } from './pages/GoalsPage';
import { SupportPage } from './pages/SupportPage';
import { ROUTES } from './routes';

/**
 * Route table. Later UI tasks add their pages here additively:
 * public routes inside the Layout, signed-in routes inside <RequireAuth>.
 */
export function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path={ROUTES.login} element={<LoginPage />} />
        <Route path="/account" element={<AccountAccessPage />} />
        <Route path={ROUTES.register} element={<RegisterPage />} />
        <Route element={<RequireAuth />}>
          <Route path="/consent" element={<ConsentPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/connections" element={<ConnectionsPage />} />
          <Route path="/trends" element={<TrendsPage />} />
          <Route path="/alerts" element={<AlertsPage />} />
          <Route path="/goals" element={<GoalsPage />} />
          <Route path="/support" element={<SupportPage />} />
        </Route>
        <Route path="/" element={<Navigate to={ROUTES.dashboard} replace />} />
        <Route path="*" element={<NotFoundRedirect />} />
      </Route>
    </Routes>
  );
}
