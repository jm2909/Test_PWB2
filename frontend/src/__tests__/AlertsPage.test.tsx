import { screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { AlertsPage } from '../pages/AlertsPage';
import { renderWithProviders } from '../test/render';

function json(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });
}

const alert = (over: Record<string, unknown>) => ({
  id: 'a1',
  metric_type: 'weight',
  event_at: '2026-11-11T07:42:00Z',
  reason: 'Your weight reading differs from your recent pattern.',
  rule_identifier: 'weight-change-pattern',
  rule_version: '1.0',
  state: 'active',
  acknowledged_at: null,
  wellness_boundary: 'This is wellness guidance, not medical advice.',
  ...over,
});

function mockApi(initial: unknown[]) {
  let items = initial as Record<string, unknown>[];
  const fetchMock = vi.fn(async (url: RequestInfo | URL, init?: RequestInit) => {
    const u = String(url);
    if (u.includes('/acknowledgements') && init?.method === 'POST') {
      items = items.map((i) =>
        u.includes(String(i.id)) ? { ...i, state: 'acknowledged', acknowledged_at: '2026-11-11T09:31:00Z' } : i,
      );
      return json(items.find((i) => u.includes(String(i.id))));
    }
    return json({ items, limit: 100, offset: 0, total: items.length });
  });
  vi.stubGlobal('fetch', fetchMock);
  return fetchMock;
}

afterEach(() => vi.unstubAllGlobals());

describe('AlertsPage', () => {
  it('shows active and acknowledged alerts with rule, time and wellness boundary', async () => {
    mockApi([
      alert({}),
      alert({ id: 'a2', metric_type: 'steps', state: 'acknowledged', acknowledged_at: '2026-11-07T08:02:00Z', rule_identifier: 'activity-pattern' }),
    ]);
    renderWithProviders(<AlertsPage />, '/alerts');
    expect(await screen.findByRole('heading', { name: 'Alerts', level: 1 })).toBeInTheDocument();
    const active = await screen.findByRole('article', { name: 'Weight change pattern' });
    expect(within(active).getByText(/weight-change-pattern · version 1.0/)).toBeInTheDocument();
    expect(within(active).getByText('Active')).toBeInTheDocument();
    expect(within(active).getByRole('button', { name: 'Acknowledge alert' })).toBeInTheDocument();
    expect(within(active).getByRole('link', { name: 'Get help with this alert' })).toHaveAttribute(
      'href',
      '/support?context=alert&id=a1',
    );
    const ack = screen.getByRole('article', { name: 'Activity pattern' });
    expect(within(ack).getByText('Acknowledged', { selector: 'span' })).toBeInTheDocument();
    expect(within(ack).queryByRole('button', { name: 'Acknowledge alert' })).not.toBeInTheDocument();
    expect(screen.getAllByText(/wellness guidance, not medical advice/)).toHaveLength(2);
  });

  it('acknowledges an alert and moves it to the acknowledged list', async () => {
    mockApi([alert({})]);
    renderWithProviders(<AlertsPage />, '/alerts');
    await userEvent.click(await screen.findByRole('button', { name: 'Acknowledge alert' }));
    expect(await screen.findByText('Alert acknowledged.')).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Acknowledge alert' })).not.toBeInTheDocument();
    expect(screen.getByRole('article', { name: 'Weight change pattern' })).toBeInTheDocument();
    expect(screen.getByText('Acknowledged', { selector: 'dt' })).toBeInTheDocument();
  });

  it('shows the empty state when no alerts are active', async () => {
    mockApi([]);
    renderWithProviders(<AlertsPage />, '/alerts');
    expect(await screen.findByText(/No active alerts right now/)).toBeInTheDocument();
    expect(screen.getByText(/creates only one active alert/)).toBeInTheDocument();
  });
});
