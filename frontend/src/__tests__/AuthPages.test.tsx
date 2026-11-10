import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import App from '../App';
import { AuthProvider } from '../lib/auth-context';

function json(status: number, body: unknown) {
  return Promise.resolve(
    new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } }),
  );
}

const session = {
  access_token: 't',
  token_type: 'bearer',
  expires_at: '2030-01-01T00:00:00Z',
  user: { id: 1, email: 'new@example.com', onboarding_status: 'not_started' },
};
const onboarding = (remaining: string[]) => ({
  profile: {},
  goal_intent: '',
  device_next_step: '',
  status: remaining.length ? 'in_progress' : 'complete',
  remaining_steps: remaining,
});

function renderAt(path: string) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <AuthProvider>
        <App />
      </AuthProvider>
    </MemoryRouter>,
  );
}

type Handler = (url: string, init?: RequestInit) => Promise<Response>;
function mockFetch(handler: Handler) {
  const spy = vi.fn((input: RequestInfo | URL, init?: RequestInit) => handler(String(input), init));
  vi.stubGlobal('fetch', spy);
  return spy;
}

afterEach(() => vi.unstubAllGlobals());

describe('Sign in', () => {
  it('is prefilled with the seed hint values and has accessible tabs', () => {
    renderAt('/login');
    expect(screen.getByRole('tablist', { name: 'Account options' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: 'Sign in' })).toHaveAttribute('aria-selected', 'true');
    expect(screen.getByLabelText('Email address')).toHaveValue('asha.menon@example.com');
    expect(screen.getByLabelText('Password')).toHaveValue('correct-horse-battery');
  });

  it('shows the 401 notice', async () => {
    mockFetch(() => json(401, { detail: 'Invalid email or password.' }));
    renderAt('/login');
    await userEvent.click(screen.getByRole('button', { name: 'Sign in' }));
    const alert = await screen.findByRole('alert');
    expect(alert).toHaveTextContent('Sign-in failed');
    expect(alert).toHaveTextContent('Email or password is incorrect.');
  });

  it('shows the 429 warning', async () => {
    mockFetch(() => json(429, { detail: 'Too many attempts. Try again later.' }));
    renderAt('/login');
    await userEvent.click(screen.getByRole('button', { name: 'Sign in' }));
    const alert = await screen.findByRole('alert');
    expect(alert).toHaveTextContent('Please wait before trying again');
    expect(alert).toHaveTextContent('Too many attempts. Try again later.');
  });

  it('goes to onboarding while steps remain', async () => {
    mockFetch((url) =>
      url.endsWith('/auth/sessions')
        ? json(200, session)
        : url.endsWith('/onboarding')
          ? json(200, onboarding(['consent']))
          : json(200, { items: [], total: 0, latest: [] }),
    );
    renderAt('/login');
    await userEvent.click(screen.getByRole('button', { name: 'Sign in' }));
    expect(await screen.findByRole('heading', { name: 'Set up FitConnect' })).toBeInTheDocument();
  });

  it('toggles password visibility', async () => {
    renderAt('/login');
    await userEvent.click(screen.getByRole('button', { name: 'Show password' }));
    expect(screen.getByLabelText('Password')).toHaveAttribute('type', 'text');
  });
});

describe('Create account', () => {
  it('rejects a short password with the 12 to 128 message without calling the API', async () => {
    const spy = mockFetch(() => json(500, {}));
    renderAt('/register');
    await userEvent.type(screen.getByLabelText('Email address'), 'a@example.com');
    await userEvent.type(screen.getByLabelText('Password'), 'short-pass');
    await userEvent.click(screen.getByRole('button', { name: /Create account/ }));
    expect(await screen.findByText('Password must be 12 to 128 characters.')).toBeInTheDocument();
    expect(spy).not.toHaveBeenCalled();
  });

  it('shows the 409 inline error with a sign-in link', async () => {
    mockFetch(() => json(409, { detail: 'exists' }));
    renderAt('/register');
    await userEvent.type(screen.getByLabelText('Email address'), 'asha.menon@example.com');
    await userEvent.type(screen.getByLabelText('Password'), 'correct-horse-battery');
    await userEvent.click(screen.getByRole('button', { name: /Create account/ }));
    expect(await screen.findByText(/An account with this email already exists\./)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Sign in instead.' })).toBeInTheDocument();
  });

  it('registers, signs in and begins onboarding', async () => {
    const spy = mockFetch((url) =>
      url.endsWith('/accounts')
        ? json(201, { id: 1, email: 'new@example.com', onboarding_status: 'not_started' })
        : url.endsWith('/auth/sessions')
          ? json(200, session)
          : url.endsWith('/onboarding')
            ? json(200, onboarding(['profile', 'goal', 'device', 'consent']))
            : json(200, { items: [], total: 0, latest: [] }),
    );
    renderAt('/register');
    await userEvent.type(screen.getByLabelText('Email address'), 'new@example.com');
    await userEvent.type(screen.getByLabelText('Password'), 'a-long-enough-pass');
    await userEvent.click(screen.getByRole('button', { name: /Create account/ }));
    expect(await screen.findByRole('heading', { name: 'Set up FitConnect' })).toBeInTheDocument();
    await waitFor(() => expect(spy).toHaveBeenCalled());
  });
});
