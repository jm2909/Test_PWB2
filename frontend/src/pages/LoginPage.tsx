import { useState } from 'react';
import type { FormEvent } from 'react';
import { Link, Navigate, useNavigate } from 'react-router-dom';
import { ApiError, api } from '../lib/api-client';
import { useAuth } from '../lib/auth-context';
import AuthTabs, { ArrowIcon } from '../components/account/AuthTabs';
import PasswordField from '../components/account/PasswordField';
import Notification from '../components/common/Notification';
import type { OnboardingData } from '../types/onboarding';

// Seed hint values: the canonical demo account (backend/app/seeds/users.py).
const SEED_EMAIL = 'asha.menon@example.com';
const SEED_PASSWORD = 'correct-horse-battery';

type Failure = { kind: 'error' | 'warning'; title: string; message: string };

export default function LoginPage() {
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState(SEED_EMAIL);
  const [password, setPassword] = useState(SEED_PASSWORD);
  const [failure, setFailure] = useState<Failure | null>(null);
  const [busy, setBusy] = useState(false);

  if (isAuthenticated && !busy) return <Navigate to="/" replace />;

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setFailure(null);
    setBusy(true);
    try {
      await login(email.trim(), password);
      let destination = '/';
      try {
        const onboarding = await api.get<OnboardingData>('/onboarding');
        if (onboarding.remaining_steps.length > 0) destination = '/onboarding';
      } catch {
        destination = '/';
      }
      navigate(destination, { replace: true });
    } catch (err) {
      if (err instanceof ApiError && err.status === 429) {
        setFailure({
          kind: 'warning',
          title: 'Please wait before trying again',
          message: 'Too many attempts. Try again later.',
        });
      } else if (err instanceof ApiError && err.status === 401) {
        setFailure({ kind: 'error', title: 'Sign-in failed', message: 'Email or password is incorrect.' });
      } else {
        setFailure({ kind: 'error', title: 'Sign-in failed', message: 'Something went wrong. Try again.' });
      }
    } finally {
      setBusy(false);
    }
  }

  return (
    <AuthTabs active="signin">
      {failure && (
        <Notification kind={failure.kind} title={failure.title} role="alert" className="mb-6">
          {failure.message}
        </Notification>
      )}
      <form onSubmit={(e) => void onSubmit(e)} noValidate aria-label="Sign in">
        <div className="mb-6">
          <label htmlFor="s-email" className="mb-2 block text-xs text-text-secondary">
            Email address
          </label>
          <input
            id="s-email"
            type="email"
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="block h-10 w-full border-0 border-b border-border-strong bg-field px-4"
          />
        </div>
        <PasswordField
          id="s-pw"
          value={password}
          onChange={setPassword}
          autoComplete="current-password"
        />
        <button
          type="submit"
          disabled={busy}
          className="inline-flex min-h-12 min-w-60 items-center justify-between gap-4 bg-button-primary px-4 text-white disabled:opacity-60"
        >
          <span>Sign in</span>
          <ArrowIcon />
        </button>
        <p className="mt-4">
          New to FitConnect?{' '}
          <Link to="/register" className="text-link">
            Create an account
          </Link>
        </p>
      </form>
    </AuthTabs>
  );
}
