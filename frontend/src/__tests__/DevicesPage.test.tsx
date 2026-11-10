import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import DevicesPage from '../pages/DevicesPage';
import { AuthProvider } from '../lib/auth-context';
import { storeSession } from '../lib/api-client';

function json(status: number, body: unknown) {
  return Promise.resolve(
    new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } }),
  );
}

const conn = (provider: string, status: string, cats: string[]) => ({
  id: provider,
  provider,
  status,
  permitted_categories: cats,
  last_successful_sync_at: null,
  failure_reason: null,
  recovery_action: null,
  last_sync_summary: null,
});

let items: ReturnType<typeof conn>[];
let consentStatus: string;
let postResult: { status: number; body: unknown };
let posts: unknown[];

beforeEach(() => {
  posts = [];
  consentStatus = 'accepted';
  items = [
    conn('wearable_platform_a', 'connected', ['sleep', 'heart_rate', 'activity']),
    conn('wearable_platform_c', 'revoked', []),
  ];
  postResult = { status: 201, body: conn('wearable_platform_c', 'connected', ['sleep', 'activity']) };
  storeSession({
    access_token: 't',
    expires_at: '2030-01-01T00:00:00Z',
    user: { id: 1, email: 'asha.menon@example.com', onboarding_status: 'complete' },
  });
  vi.stubGlobal(
    'fetch',
    vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith('/device-connections') && init?.method === 'POST') {
        posts.push(JSON.parse(String(init.body)));
        return json(postResult.status, postResult.body);
      }
      if (url.endsWith('/device-connections')) return json(200, { items, total: items.length });
      return json(200, {
        items: [],
        total: 0,
        latest: [{ id: 'c', purpose: 'device_processing', version: '1.0', status: consentStatus, recorded_at: '2026-01-01T00:00:00Z' }],
      });
    }),
  );
});
afterEach(() => vi.unstubAllGlobals());

function renderPage() {
  return render(
    <MemoryRouter>
      <AuthProvider>
        <DevicesPage />
      </AuthProvider>
    </MemoryRouter>,
  );
}

describe('DevicesPage', () => {
  it('shows each wearable state and the scale ready to pair', async () => {
    renderPage();
    expect(await screen.findByRole('heading', { level: 1, name: 'Devices' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Pair scale/ })).toBeInTheDocument();
    expect(screen.getByText('Revoked', { exact: true })).toBeInTheDocument();
    expect(screen.getByText('Not connected')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'View sync status' })).toHaveAttribute('href', '/devices/sync');
    expect(screen.getByRole('button', { name: 'Connect' })).toBeInTheDocument();
    expect(screen.queryByText('Device connection is paused')).not.toBeInTheDocument();
  });

  it('reconnects platform C and shows the categories the backend returned', async () => {
    renderPage();
    await userEvent.click(await screen.findByRole('button', { name: 'Reconnect' }));
    expect(posts).toEqual([{ provider: 'wearable_platform_c', connection_mode: 'authorize' }]);
    const row = (await screen.findByText('Wearable platform C')).closest('li') as HTMLElement;
    expect(await within(row).findByText('Connected')).toBeInTheDocument();
    expect(within(row).getByText('Sleep')).toBeInTheDocument();
    expect(within(row).getByText('Activity')).toBeInTheDocument();
  });

  it('shows the pairing failure and a Try again action', async () => {
    postResult = { status: 201, body: { ...conn('sapphire_scale', 'failed', []), recovery_action: 'Try again' } };
    renderPage();
    await userEvent.click(await screen.findByRole('button', { name: /Pair scale/ }));
    expect(await screen.findByText('Scale not paired')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Try again' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Pairing tips' })).toBeInTheDocument();
  });

  it('shows the paired scale with its categories', async () => {
    items.push(conn('sapphire_scale', 'connected', ['weight', 'body_fat']));
    renderPage();
    expect(await screen.findByText('Weight')).toBeInTheDocument();
    expect(screen.getByText('Body fat %')).toBeInTheDocument();
  });

  it('shows the consent-paused notice and disables connecting when device processing is declined', async () => {
    consentStatus = 'declined';
    renderPage();
    expect(await screen.findByText('Device connection is paused')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Review consent' })).toHaveAttribute('href', '/onboarding');
    expect(screen.getByRole('button', { name: 'Connect' })).toBeDisabled();
  });
});
