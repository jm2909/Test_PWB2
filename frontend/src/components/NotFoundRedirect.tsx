import { Navigate } from 'react-router-dom';
import { useAuth } from '../lib/auth-context';
import { ROUTES } from '../routes';

/** Unknown paths go to "/", which resolves to the dashboard (signed in) or sign-in. */
export function NotFoundRedirect() {
  const { user } = useAuth();
  return <Navigate to={user ? ROUTES.dashboard : ROUTES.login} replace />;
}
