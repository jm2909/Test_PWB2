import { screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { TrendsPage } from '../pages/TrendsPage';
import { renderWithProviders } from '../test/render';

function json(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });
}

const weight = {
  metric_type: 'weight',
  unit: 'kg',
  range: '30d',
  range_label: 'Last 30 days',
  status: 'available',
  explanation: null,
  points: [
    { captured_at: '2026-10-12T07:00:00Z', value: '73.6' },
    { captured_at: '2026-11-01T07:00:00Z', value: '72.9' },
    { captured_at: '2026-11-11T07:00:00Z', value: '72.4' },
  ],
};
const steps = {
  metric_type: 'steps',
  unit: 'count',
  range: '365d',
  range_label: 'Last 365 days',
  status: 'insufficient_data',
  explanation: 'Only 4 readings are available; at least 10 are needed.',
  points: [],
};
const insight = {
  id: 'i1',
  metric_type: 'weight',
  observation_period: { start: '2026-10-12T00:00:00Z', end: '2026-11-11T00:00:00Z' },
  observation: 'Your recorded weight went from 73.6 kg to 72.4 kg.',
  wellness_guidance: 'Small, steady changes are common.',
  uncertainty: 'Some uncertainty.',
  created_at: '2026-11-11T08:00:00Z',
};
const page = (items: unknown[]) => ({ items, limit: 100, offset: 0, total: items.length });

function mockApi(extra: { connections?: unknown[] } = {}) {
  return vi.spyOn(globalThis, 'fetch').mockImplementation((input) => {
    const url = String(input);
    if (url.includes('/v1/trends/steps')) return Promise.resolve(json(steps));
    if (url.includes('/v1/trends/')) return Promise.resolve(json(weight));
    if (url.includes('/v1/insights')) return Promise.resolve(json(page([insight])));
    if (url.includes('/v1/connections')) return Promise.resolve(json(page(extra.connections ?? [])));
    return Promise.resolve(json({ detail: 'not found' }, 404));
  });
}

afterEach(() => vi.restoreAllMocks());

describe('TrendsPage', () => {
  it('shows the weight trend table with unit, range and source', async () => {
    mockApi();
    renderWithProviders(<TrendsPage />, '/trends');
    expect(await screen.findByRole('heading', { name: 'Weight over the last 30 days' })).toBeInTheDocument();
    const table = await screen.findByRole('table');
    expect(within(table).getAllByRole('row')).toHaveLength(4);
    expect(within(table).getByRole('columnheader', { name: 'Weight (kg)' })).toBeInTheDocument();
    expect(screen.getByText(/Unit: kilograms \(kg\)/)).toBeInTheDocument();
    expect(screen.getByRole('img', { name: /Weight/ })).toBeInTheDocument();
    expect(await screen.findByRole('heading', { name: 'What we measured' })).toBeInTheDocument();
  });

  it('explains insufficient data instead of implying a trend', async () => {
    mockApi();
    renderWithProviders(<TrendsPage />, '/trends');
    await screen.findByRole('table');
    await userEvent.selectOptions(screen.getByLabelText('Metric'), 'steps');
    await userEvent.click(screen.getByLabelText('365 days'));
    expect(await screen.findByText('Not enough data to show a trend')).toBeInTheDocument();
    expect(screen.getByText(/at least 10 are needed/)).toBeInTheDocument();
    expect(screen.queryByRole('table')).not.toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'check your connections' })).toHaveAttribute('href', '/connections');
  });

  it('warns when the metric source is stale', async () => {
    mockApi({
      connections: [
        {
          id: 'c1',
          source: 'scale',
          provider: 'sapphire-scale',
          display_label: 'Bedroom',
          status: 'stale',
          last_successful_sync_at: '2026-11-03T06:58:00Z',
          recovery_action: 'retry_sync',
        },
      ],
    });
    renderWithProviders(<TrendsPage />, '/trends');
    expect(await screen.findByText(/comes from a source that is out of date/)).toBeInTheDocument();
  });
});
