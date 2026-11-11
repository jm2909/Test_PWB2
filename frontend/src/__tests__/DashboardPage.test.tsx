import { screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { DashboardPage } from '../pages/DashboardPage';
import { renderWithProviders } from '../test/render';

function json(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });
}

const alertRow = (over: Record<string, unknown>) => ({
  id: 'a1',
  metric_type: 'weight',
  event_at: '2026-11-11T07:42:00Z',
  reason: 'Pattern',
  rule_identifier: 'weight-change-pattern',
  rule_version: '1.0',
  state: 'active',
  acknowledged_at: null,
  wellness_boundary: 'Not medical advice.',
  ...over,
});

const FULL = {
  measurements: [
    { metric_type: 'weight', value: '68.4', unit: 'kg', source: 'scale', captured_at: '2026-11-11T07:42:00Z', status: 'current' },
  ],
  source_statuses: [
    { id: 's1', source: 'scale', provider: 'sapphire-scale', display_label: 'Bedroom', status: 'stale', last_successful_sync_at: '2026-11-03T06:58:00Z' },
    { id: 's2', source: 'wearable', provider: 'fitband', display_label: 'Provider A', status: 'pending', last_successful_sync_at: null },
  ],
  alerts: [alertRow({})],
  goals: [
    { id: 'g1', category: 'weight_management', metric_type: 'weight', target_value: '65', target_unit: 'kg', target_date: '2027-01-31', state: 'active', progress_status: 'available', current_value: '68.4' },
    { id: 'g2', category: 'activity', metric_type: 'steps', target_value: '8000', target_unit: 'count', target_date: '2027-01-31', state: 'active', progress_status: 'data_gap', current_value: null },
  ],
  insights: [
    { id: 'i1', metric_type: 'steps', status: 'available', observation_period_start: null, observation_period_end: null, observation: 'Average steps rose.', wellness_guidance: 'Keep walking.', uncertainty: 'Based on 5 of 7 days.' },
  ],
  unavailable_categories: [],
};

function mockApi(dashboard: unknown, alerts: unknown[]) {
  vi.stubGlobal(
    'fetch',
    vi.fn(async (url: RequestInfo | URL) => {
      const u = String(url);
      if (u.includes('/v1/alerts')) return json({ items: alerts, limit: 100, offset: 0, total: alerts.length });
      if (u.includes('/v1/dashboard')) return json(dashboard);
      return json({ detail: 'nope' }, 404);
    }),
  );
}

afterEach(() => vi.unstubAllGlobals());

describe('DashboardPage', () => {
  it('shows readings, unavailable categories, source status, alerts, goals and insight', async () => {
    mockApi(FULL, [
      alertRow({}),
      alertRow({ id: 'a2', metric_type: 'steps', state: 'acknowledged', acknowledged_at: '2026-11-07T08:02:00Z' }),
    ]);
    renderWithProviders(<DashboardPage />, '/dashboard');

    expect(screen.getByRole('heading', { name: 'Your wellness dashboard', level: 1 })).toBeInTheDocument();
    const weight = await screen.findByRole('article', { name: 'Weight' });
    expect(within(weight).getByText('68.4')).toBeInTheDocument();
    expect(within(weight).getByText('Sapphire scale')).toBeInTheDocument();
    expect(within(screen.getByRole('article', { name: 'Sleep' })).getByText('Unavailable')).toBeInTheDocument();
    expect(screen.getByText(/Unavailable categories: Steps, Sleep, Active time/)).toBeInTheDocument();

    const table = screen.getByRole('table');
    expect(within(table).getByText('Stale')).toBeInTheDocument();
    expect(within(table).getByText('Pending')).toBeInTheDocument();
    expect(within(table).getByText('No successful sync yet')).toBeInTheDocument();

    const items = screen.getAllByRole('listitem').filter((li) => li.hasAttribute('data-state'));
    expect(items.map((li) => li.getAttribute('data-state'))).toEqual(['active', 'acknowledged']);

    expect(screen.getByText(/Progress available: current 68.4 kg/)).toBeInTheDocument();
    expect(screen.getByText('Data gap')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Steps · last 7 days' })).toBeInTheDocument();
  });

  it('shows explicit unavailable states for every category when there is no data', async () => {
    mockApi({ ...FULL, measurements: [], source_statuses: [], alerts: [], goals: [], insights: [] }, []);
    renderWithProviders(<DashboardPage />, '/dashboard');
    await screen.findByText(/Unavailable categories/);
    expect(screen.getAllByText('Unavailable')).toHaveLength(4);
    expect(screen.getByText('No sources are connected yet.')).toBeInTheDocument();
    expect(screen.getByText('No alerts right now.')).toBeInTheDocument();
  });

  it('simplified view hides detail but keeps alerts and source status', async () => {
    mockApi(FULL, [alertRow({})]);
    renderWithProviders(<DashboardPage />, '/dashboard');
    await screen.findByRole('article', { name: 'Weight' });
    await userEvent.click(screen.getByRole('button', { name: 'Simplified view' }));
    expect(screen.queryByText('Recorded')).not.toBeInTheDocument();
    expect(screen.queryByRole('heading', { name: 'Goal progress' })).not.toBeInTheDocument();
    expect(screen.queryByRole('heading', { name: 'Insight' })).not.toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Alerts' })).toBeInTheDocument();
    expect(screen.getByRole('table')).toBeInTheDocument();
  });
});
