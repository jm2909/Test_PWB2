import { useState } from 'react';
import type { FormEvent } from 'react';
import { Link, Navigate, useNavigate } from 'react-router-dom';
import { ApiError, api } from '../lib/api-client';
import { useAuth } from '../lib/auth-context';
import AuthTabs, { ArrowIcon } from '../components/account/AuthTabs';
import PasswordField from '../components/account/PasswordField';

const PASSWORD_RULE = 'Password must be 12 to 128 characters.';

export default function RegisterPage() {
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [emailError, setEmailError] = useState<'duplicate' | string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  if (isAuthenticated && !busy) return <Navigate to="/" replace />;

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setEmailError(null);
    setPasswordError(null);
    setFormError(null);
    if (password.length < 12 || password.length > 128) {
      setPasswordError(PASSWORD_RULE);
      return;
    }
    setBusy(true);
    try {
      await api.post('/accounts', { email: email.trim(), password });
      await login(email.trim(), password);
      navigate('/onboarding', { replace: true });
    } catch (err) {
      if (err instanceof ApiError && err.status === 409) {
        setEmailError('duplicate');
      } else if (err instanceof ApiError && err.status === 422) {
        if (/email/i.test(err.detail) && !/password/i.test(err.detail)) {
          setEmailError('Enter a valid email address.');
        } else {
          setPasswordError(PASSWORD_RULE);
        }
      } else {
        setFormError('Something went wrong. Try again.');
      }
    } finally {
      setBusy(false);
    }
  }

  return (
    <AuthTabs active="create">
      {formError && (
        <p role="alert" className="mb-6 text-text-error">
          {formError}
        </p>
      )}
      <form onSubmit={(e) => void onSubmit(e)} noValidate aria-label="Create account">
        <div className="mb-6">
          <label htmlFor="c-email" className="mb-2 block text-xs text-text-secondary">
            Email address
          </label>
          <input
            id="c-email"
            type="email"
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            aria-invalid={emailError ? true : undefined}
            aria-describedby={emailError ? 'c-email-e' : undefined}
            className={`block h-10 w-full border-0 border-b bg-field px-4 ${
              emailError ? 'border-b-transparent outline outline-2 -outline-offset-2 outline-support-error' : 'border-border-strong'
            }`}
          />
          {emailError && (
            <p id="c-email-e" className="mt-1 flex items-start gap-1 text-xs text-text-error">
              <svg width="16" height="16" viewBox="0 0 16 16" className="fill-support-error" aria-hidden="true">
                <path d="M8,1C4.1,1,1,4.1,1,8s3.1,7,7,7s7-3.1,7-7S11.9,1,8,1z M10.7,11.5L4.5,5.3l0.8-0.8l6.2,6.2L10.7,11.5z" />
              </svg>
              {emailError === 'duplicate' ? (
                <span>
                  An account with this email already exists.{' '}
                  <Link to="/login" className="text-link">
                    Sign in instead.
                  </Link>
                </span>
              ) : (
                <span>{emailError}</span>
              )}
            </p>
          )}
        </div>
        <PasswordField
          id="c-pw"
          value={password}
          onChange={setPassword}
          autoComplete="new-password"
          helper="Use 12 to 128 characters."
          error={passwordError}
        />
        <button
          type="submit"
          disabled={busy}
          className="inline-flex min-h-12 min-w-60 items-center justify-between gap-4 bg-button-primary px-4 text-white disabled:opacity-60"
        >
          <span>Create account</span>
          <ArrowIcon />
        </button>
        <p className="mt-4">
          Already have an account?{' '}
          <Link to="/login" className="text-link">
            Sign in
          </Link>
        </p>
      </form>
    </AuthTabs>
  );
}
