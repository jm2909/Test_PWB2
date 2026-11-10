import { act, render, screen } from '@testing-library/react';
import { AuthProvider, useAuth } from '../lib/auth-context';
import { getStoredSession } from '../lib/api-client';

function Probe() {
  const { user, login, logout } = useAuth();
  return (
    <div>
      <p>{user ? `in:${user.email}` : 'out'}</p>
      <button onClick={() => void login('a@example.com', 'pw').catch(() => undefined)}>go</button>
      <button onClick={() => void logout()}>leave</button>
    </div>
  );
}

function stubFetch(responses: Response[]) {
  const fn = vi.fn();
  responses.forEach((r) => fn.mockResolvedValueOnce(r));
  vi.stubGlobal('fetch', fn);
  return fn;
}

const json = (status: number, body: unknown) =>
  new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });

afterEach(() => vi.unstubAllGlobals());

describe('AuthProvider', () => {
  it('logs in, persists the session, and logs out', async () => {
    const fetchMock = stubFetch([
      json(200, {
        access_token: 'tok',
        token_type: 'bearer',
        expires_at: '2030-01-01T00:00:00Z',
        user: { id: 1, email: 'a@example.com', onboarding_status: 'complete' },
      }),
      new Response(null, { status: 204 }),
    ]);
    render(
      <AuthProvider>
        <Probe />
      </AuthProvider>,
    );
    expect(screen.getByText('out')).toBeInTheDocument();

    await act(async () => screen.getByRole('button', { name: 'go' }).click());
    expect(await screen.findByText('in:a@example.com')).toBeInTheDocument();
    expect(getStoredSession()?.access_token).toBe('tok');
    expect((fetchMock.mock.calls[0] as [string])[0]).toBe('/api/v1/auth/sessions');

    await act(async () => screen.getByRole('button', { name: 'leave' }).click());
    expect(await screen.findByText('out')).toBeInTheDocument();
    expect(getStoredSession()).toBeNull();
    expect((fetchMock.mock.calls[1] as [string])[0]).toBe('/api/v1/auth/sessions/current');
  });

  it('stays signed out when credentials are rejected', async () => {
    stubFetch([json(401, { detail: 'Invalid credentials' })]);
    render(
      <AuthProvider>
        <Probe />
      </AuthProvider>,
    );
    await act(async () => screen.getByRole('button', { name: 'go' }).click());
    expect(screen.getByText('out')).toBeInTheDocument();
    expect(getStoredSession()).toBeNull();
  });
});
