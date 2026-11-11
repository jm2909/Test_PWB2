import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Route, Routes } from 'react-router-dom';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { LoginPage } from '../pages/LoginPage';
import { RequireAuth } from '../components/auth/RequireAuth';
import { renderWithProviders } from '../test/render';
import { DEMO_ASHA_EMAIL, DEMO_PASSWORD } from '../lib/demo-credentials';

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });
}

function tree() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<RequireAuth />}>
        <Route path="/dashboard" element={<h1>Dash</h1>} />
      </Route>
    </Routes>
  );
}

afterEach(() => vi.restoreAllMocks());

describe('LoginPage', () => {
  it('redirects unauthenticated visitors to the login form', () => {
    renderWithProviders(tree(), '/dashboard');
    expect(screen.getByRole('button', { name: 'Sign in' })).toBeInTheDocument();
  });

  it('signs in through /api/v1/auth/tokens and stores the session', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      jsonResponse(
        {
          access_token: 'tok',
          token_type: 'bearer',
          expires_at: '2030-01-01T00:00:00Z',
          account: { id: '1', email: DEMO_ASHA_EMAIL, display_name: 'Asha', next_step: 'consent_setup', created_at: '2026-01-01T00:00:00Z' },
        },
        201,
      ),
    );
    renderWithProviders(tree(), '/login');
    await userEvent.type(screen.getByLabelText('Email address'), DEMO_ASHA_EMAIL);
    await userEvent.type(screen.getByLabelText('Password'), DEMO_PASSWORD);
    await userEvent.click(screen.getByRole('button', { name: 'Sign in' }));
    expect(await screen.findByRole('heading', { name: 'Dash' })).toBeInTheDocument();
    expect(fetchMock.mock.calls[0][0]).toBe('/api/v1/auth/tokens');
    expect(window.sessionStorage.getItem('fitconnect.token')).toBe('tok');
  });

  it('shows the uniform invalid-credentials message', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(jsonResponse({ detail: 'Invalid credentials' }, 401));
    renderWithProviders(tree(), '/login');
    await userEvent.type(screen.getByLabelText('Email address'), 'x@example.com');
    await userEvent.type(screen.getByLabelText('Password'), 'whatever-password');
    await userEvent.click(screen.getByRole('button', { name: 'Sign in' }));
    await waitFor(() => expect(screen.getByRole('alert')).toHaveTextContent('Invalid credentials.'));
  });

  it('shows the too-many-attempts state and disables sign in on 429', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(jsonResponse({ detail: 'Too many requests' }, 429));
    renderWithProviders(tree(), '/login');
    await userEvent.type(screen.getByLabelText('Email address'), 'x@example.com');
    await userEvent.type(screen.getByLabelText('Password'), 'whatever-password');
    await userEvent.click(screen.getByRole('button', { name: 'Sign in' }));
    expect(await screen.findByText('Too many sign-in attempts.')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Sign in' })).toBeDisabled();
  });

  it('shows the signed-out notice after sign out', () => {
    renderWithProviders(tree(), { pathname: '/login', state: { signedOut: true } });
    expect(screen.getByText('You have signed out.')).toBeInTheDocument();
  });
});
