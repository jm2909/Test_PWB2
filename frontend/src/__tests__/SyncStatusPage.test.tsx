import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import SyncStatusPage from '../pages/SyncStatusPage';
import { AuthProvider } from '../lib/auth-context';
import { storeSession } from '../lib/api-client';

function json(status: number, body: unknown) {
  return Promise.resolve(
    new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } }),
  );
}

const conn = (id: string, provider: string, status: string, reason: string | null = null) => ({
  id,
  provider,
  status,
  permitted_categories: ['sleep'],
  last_successful_sync_at: '2020-01-01T10:00:00Z',
  failure_reason: reason,
  recovery_action: null,
  last_sync_summary: null,
});

let syncCalls: { body: unknown; key: string | null }[];

beforeEach(() => {
  syncCalls = [];
  storeSession({
    access_token: 't',
    expires_at: '2030-01-01T00:00:00Z',
    user: { id: 1, email: 'asha.menon@example.com', onboarding_status: 'complete' },
  });
  vi.stubGlobal(
    'fetch',
    vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith('/sync') && init?.method === 'POST') {
        const headers = init.headers as Record<string, string>;
        syncCalls.push({ body: JSON.parse(String(init.body)), key: headers['Idempotency-Key'] ?? null });
        return json(200, {
          ...conn('b', 'wearable_platform_b', 'connected'),
          last_sync_summary: { new_readings: 14, by_metric: { weight: 1, steps: 13 }, duplicates: 2 },
        });
      }
      if (url.endsWith('/device-connections')) {
        return json(200, {
          items: [
            conn('s', 'sapphire_scale', 'connected'),
            conn('b', 'wearable_platform_b', 'failed', 'The provider did not respond.'),
            conn('c', 'wearable_platform_c', 'revoked', 'Access was revoked at the provider.'),
          ],
          total: 3,
        });
      }
      return json(404, { detail: 'Not found' });
    }),
  );
});

function renderPage() {
  return render(
    <MemoryRouter>
      <AuthProvider>
        <SyncStatusPage />
      </AuthProvider>
    </MemoryRouter>,
  );
}

describe('SyncStatusPage', () => {
  it('lists connections with state-specific actions and never shows failed as current', async () => {
    renderPage();
    const table = await screen.findByRole('table');
    expect(within(table).getByRole('button', { name: /Sync now/ })).toBeInTheDocument();
    expect(within(table).getByRole('button', { name: /Retry/ })).toBeInTheDocument();
    expect(within(table).getByRole('button', { name: /Reconnect/ })).toBeInTheDocument();
    expect(within(table).getByText('Failed')).toBeInTheDocument();
    expect(screen.getByText('Sync failed for Wearable platform B')).toBeInTheDocument();
  });

  it('retries with an idempotency key and shows the returned summary', async () => {
    renderPage();
    await userEvent.click(await screen.findByRole('button', { name: /Retry/ }));
    expect(await screen.findByText('Sync complete. 14 new readings added.')).toBeInTheDocument();
    expect(syncCalls).toHaveLength(1);
    expect(syncCalls[0].body).toEqual({ device_connection_id: 'b' });
    expect((syncCalls[0].key ?? '').length).toBeGreaterThanOrEqual(16);
    expect(screen.getByTestId('added-count')).toHaveTextContent('14');
    expect(screen.getByText('Steps: 13')).toBeInTheDocument();
    expect(screen.getByText('2 readings were received twice and counted once.')).toBeInTheDocument();
  });
});
