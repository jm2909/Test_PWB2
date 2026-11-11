import { useState } from 'react';
import type { FormEvent } from 'react';
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { Notice } from '../ui/Notice';
import { ApiError } from '../../types/api';
import { DEMO_ASHA_EMAIL, DEMO_PASSWORD } from '../../lib/demo-credentials';
import { useAuth } from '../../lib/auth-context';
import { ROUTES } from '../../routes';

interface LocationState {
  from?: string;
  signedOut?: boolean;
}

/** The "Sign in" tile of the account-access wireframe, with all its states. */
export function SignInForm() {
  const { user, login, sessionTimedOut } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<ApiError | null>(null);
  const [busy, setBusy] = useState(false);

  if (user) {
    const from = (location.state as LocationState | null)?.from;
    return <Navigate to={from ?? ROUTES.dashboard} replace />;
  }

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    setBusy(true);
    try {
      await login({ email: email.trim(), password });
      const from = (location.state as LocationState | null)?.from;
      navigate(from ?? ROUTES.dashboard, { replace: true });
    } catch (err) {
      setError(err instanceof ApiError ? err : new ApiError(0, 'Sign in failed. Try again.'));
      setBusy(false);
    }
  };

  const tooMany = error?.status === 429;
  const signedOut = (location.state as LocationState | null)?.signedOut === true && !sessionTimedOut;

  return (
    <div className="tile">
      <h2 id="sign-h" className="!mb-3 text-base font-semibold">
        Sign in
      </h2>
      {signedOut && (
        <div className="mb-4">
          <Notice kind="info" title="You have signed out.">
            <p>Your session has ended on this device.</p>
          </Notice>
        </div>
      )}
      {sessionTimedOut && (
        <div className="mb-4">
          <Notice kind="warning" role="status">
            <p>
              You were away for a while. To protect your privacy, your wellness data is hidden until you
              sign in again.
            </p>
          </Notice>
        </div>
      )}
      <form noValidate aria-labelledby="sign-h" onSubmit={onSubmit}>
        <div className="mb-6">
          <label className="field-label" htmlFor="sign-email">
            Email address
          </label>
          <input
            className="field-input"
            id="sign-email"
            name="email"
            type="email"
            autoComplete="username"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>
        <div className="mb-6">
          <label className="field-label" htmlFor="sign-pw">
            Password
          </label>
          <input
            className="field-input"
            id="sign-pw"
            name="password"
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            aria-describedby="sign-pw-help"
          />
          <p className="field-help" id="sign-pw-help">
            Passwords are never displayed.
          </p>
        </div>
        {error && !tooMany && (
          <div className="mb-4">
            <Notice kind="error" title={error.status === 401 ? 'Invalid credentials.' : 'Sign in failed.'}>
              <p>
                {error.status === 401
                  ? 'Check your email address and password, then try again.'
                  : error.detail}
              </p>
            </Notice>
          </div>
        )}
        {tooMany && (
          <div className="mb-4">
            <Notice kind="warning" title="Too many sign-in attempts.">
              <p>Wait a few minutes before trying again. The sign-in button is unavailable until then.</p>
            </Notice>
          </div>
        )}
        <button className="btn" type="submit" disabled={busy || tooMany}>
          {sessionTimedOut ? 'Sign in again' : 'Sign in'}
        </button>
      </form>
      <p className="field-help mt-4">
        New here? <Link to={ROUTES.register}>Create an account</Link>
      </p>
      {import.meta.env.DEV && (
        <p className="field-help mt-4">
          Demo account: {DEMO_ASHA_EMAIL} / {DEMO_PASSWORD}
        </p>
      )}
    </div>
  );
}
