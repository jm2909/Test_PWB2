import { screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { ConnectionsPage } from '../pages/ConnectionsPage';
import { renderWithProviders } from '../test/render';

function json(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });
}

const consent = {
  id: '1',
  decision: 'granted',
  notice_version: 'v1.0',
  recorded_at: '2026-11-11T09:14:00Z',
  collection_allowed: true,
  data_rights_path: null,
};
const providers = [
  { provider: 'fitband', display_name: 'Fitband', authorization_mode: 'oauth' },
  { provider: 'pulsewear', display_name: 'Pulsewear', authorization_mode: 'oauth' },
];
const conn = (over: Record<string, unknown>) => ({
  id: 'x',
  source: 'scale',
  provider: null,
  display_label: 'Bathroom',
  status: 'current',
  last_successful_sync_at: '2026-11-11T07:42:00Z',
  recovery_action: null,
  ...over,
});
const items = [
  conn({ id: 'c1' }),
  conn({
    id: 'c2',
    display_label: 'Bedroom',
    status: 'stale',
    last_successful_sync_at: '2026-11-03T06:58:00Z',
    recovery_action: 'retry_sync',
  }),
  conn({
    id: 'c3',
    source: 'wearable',
    provider: 'fitband',
    display_label: 'Provider B',
    status: 'failed',
    recovery_action: 'retry',
  }),
  conn({
    id: 'c4',
    source: 'wearable',
    provider: 'pulsewear',
    display_label: 'Provider A',
    status: 'pending',
    last_successful_sync_at: null,
  }),
];

function mockApi(consentBody: unknown, consentStatus = 200) {
  return vi.spyOn(globalThis, 'fetch').mockImplementation((input, init) => {
    const url = String(input);
    if (url.includes('/v1/consents')) return Promise.resolve(json(consentBody, consentStatus));
    if (url.includes('/connections/providers')) return Promise.resolve(json(providers));
    if (url.includes('/connections/scale') && init?.method === 'POST') {
      return Promise.resolve(json(conn({ id: 'c9', display_label: 'Living room' }), 201));
    }
    if (url.includes('/v1/connections')) {
      return Promise.resolve(json({ items, limit: 100, offset: 0, total: items.length }));
    }
    return Promise.resolve(json({ detail: 'nope' }, 404));
  });
}

afterEach(() => vi.restoreAllMocks());

describe('ConnectionsPage', () => {
  it('blocks connecting when consent is not granted', async () => {
    mockApi({ detail: 'none' }, 404);
    renderWithProviders(<ConnectionsPage />, '/connections');
    expect(await screen.findByText('Active consent is required before connecting a source.')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Connect scale' })).toBeDisabled();
    expect(screen.getByRole('button', { name: 'Authorize and connect' })).toBeDisabled();
  });

  it('shows each status with icon text, notices and recovery actions', async () => {
    mockApi(consent);
    renderWithProviders(<ConnectionsPage />, '/connections');
    const stale = await screen.findByRole('article', { name: 'Sapphire Smart Scale – Bedroom' });
    expect(within(stale).getByText('Stale')).toBeInTheDocument();
    expect(within(stale).getByText(/3 Nov 2026/)).toBeInTheDocument();
    expect(within(stale).getByRole('button', { name: 'Retry sync' })).toBeInTheDocument();
    expect(within(stale).getByRole('link', { name: 'Contact support' })).toHaveAttribute(
      'href',
      '/support?context=device&id=c2',
    );
    const failed = screen.getByRole('article', { name: 'Provider B' });
    expect(within(failed).getByText('Failed')).toBeInTheDocument();
    expect(within(failed).getByRole('button', { name: 'Retry' })).toBeInTheDocument();
    const pending = screen.getByRole('article', { name: 'Provider A' });
    expect(within(pending).getByText('No successful sync yet')).toBeInTheDocument();
    expect(within(pending).getByRole('button', { name: 'Refresh status' })).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Disconnect' })).not.toBeInTheDocument();
  });

  it('connects a scale with its identifier', async () => {
    const fetchMock = mockApi(consent);
    renderWithProviders(<ConnectionsPage />, '/connections');
    await screen.findByRole('article', { name: 'Provider A' });
    await userEvent.selectOptions(screen.getByLabelText('Choose your scale'), 'SSC-0733');
    await userEvent.click(screen.getByRole('button', { name: 'Connect scale' }));
    expect(await screen.findByText('Scale connected.')).toBeInTheDocument();
    const post = fetchMock.mock.calls.find(
      ([u, i]) => String(u).includes('/connections/scale') && i?.method === 'POST',
    );
    expect(JSON.parse(String(post?.[1]?.body))).toEqual({
      device_identifier: 'SSC-0733',
      device_label: 'Living room',
    });
  });
});
