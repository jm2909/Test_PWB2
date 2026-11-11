import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../../lib/auth-context';
import { ROUTES } from '../../routes';

/** The only route guard: unauthenticated visitors go to /login and come back afterwards. */
export function RequireAuth() {
  const { user } = useAuth();
  const location = useLocation();
  if (!user) {
    return <Navigate to={ROUTES.login} replace state={{ from: location.pathname }} />;
  }
  return <Outlet />;
}
