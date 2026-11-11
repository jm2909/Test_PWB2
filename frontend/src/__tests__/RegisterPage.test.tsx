import { screen } from '@testing-library/react';
import { Route, Routes } from 'react-router-dom';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { RegisterPage } from '../pages/RegisterPage';
import { renderWithProviders } from '../test/render';

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });
}

async function fill(name: string, email: string, pw: string) {
  await userEvent.type(screen.getByLabelText('Display name'), name);
  await userEvent.type(screen.getByLabelText('Email address'), email);
  await userEvent.type(screen.getByLabelText('Password'), pw);
  await userEvent.click(screen.getByRole('button', { name: 'Create account' }));
}

afterEach(() => vi.restoreAllMocks());

describe('RegisterPage', () => {
  it('shows field errors and does not call the API for invalid input', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch');
    renderWithProviders(<RegisterPage />, '/register');
    await fill('Asha', 'asha.example.com', 'short');
    expect(screen.getByText('Enter a valid email address, such as name@example.com.')).toBeInTheDocument();
    expect(screen.getByText('Password must be between 12 and 128 characters.')).toBeInTheDocument();
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('registers, signs in and continues to consent setup', async () => {
    const account = { id: '1', email: 'a@example.com', display_name: 'Asha', next_step: 'consent_setup', created_at: '2026-01-01T00:00:00Z' };
    const fetchMock = vi
      .spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce(jsonResponse(account, 201))
      .mockResolvedValueOnce(
        jsonResponse({ access_token: 'tok', token_type: 'bearer', expires_at: '2030-01-01T00:00:00Z', account }, 201),
      );
    renderWithProviders(
      <Routes>
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/consent" element={<h1>Consent page</h1>} />
      </Routes>,
      '/register',
    );
    await fill('Asha', 'a@example.com', 'long-enough-password');
    expect(await screen.findByRole('heading', { name: 'Consent page' })).toBeInTheDocument();
    expect(fetchMock.mock.calls[0][0]).toBe('/api/v1/auth/accounts');
    expect(fetchMock.mock.calls[1][0]).toBe('/api/v1/auth/tokens');
  });

  it('shows the duplicate-email message', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(jsonResponse({ detail: 'Email already registered' }, 400));
    renderWithProviders(<RegisterPage />, '/register');
    await fill('Asha', 'a@example.com', 'long-enough-password');
    expect(await screen.findByRole('alert')).toHaveTextContent('Account not created.');
  });
});
