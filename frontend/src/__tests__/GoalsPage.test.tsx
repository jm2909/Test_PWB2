import { screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { GoalsPage } from '../pages/GoalsPage';
import { renderWithProviders } from '../test/render';

function json(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });
}

const goal = (over: Record<string, unknown>) => ({
  id: 'g1',
  state: 'active',
  category: 'weight_management',
  metric_type: 'weight',
  target_value: '70.0000',
  target_unit: 'kg',
  target_date: '2027-01-31',
  progress_status: 'available',
  current_value: '72.4000',
  ...over,
});

function mockApi(initial: Record<string, unknown>[]) {
  let items = initial;
  const fetchMock = vi.fn(async (url: RequestInfo | URL, init?: RequestInit) => {
    const u = String(url);
    if (init?.method === 'POST') {
      const body = JSON.parse(String(init.body)) as Record<string, unknown>;
      items = [...items, goal({ id: 'new', ...body, target_value: String(body.target_value), progress_status: 'data_gap', current_value: null })];
      return json(items[items.length - 1], 201);
    }
    if (init?.method === 'PATCH') {
      const body = JSON.parse(String(init.body)) as { state: string };
      items = items.map((i) => (u.endsWith(String(i.id)) ? { ...i, state: body.state } : i));
      return json(items.find((i) => u.endsWith(String(i.id))));
    }
    return json({ items, limit: 100, offset: 0, total: items.length });
  });
  vi.stubGlobal('fetch', fetchMock);
  return fetchMock;
}

afterEach(() => vi.unstubAllGlobals());

describe('GoalsPage', () => {
  it('shows progress when available and a data gap otherwise', async () => {
    mockApi([goal({}), goal({ id: 'g2', category: 'fitness', metric_type: 'steps', target_value: '8000', target_unit: 'count', progress_status: 'data_gap', current_value: null })]);
    renderWithProviders(<GoalsPage />, '/goals');
    const weight = await screen.findByRole('article', { name: 'Weight management · Weight to 70 kg' });
    expect(within(weight).getByText(/current 72.4 kg/)).toBeInTheDocument();
    const steps = screen.getByRole('article', { name: 'Fitness · 8,000 steps per day' });
    expect(within(steps).getAllByText(/Data gap/).length).toBeGreaterThan(0);
    expect(within(steps).queryByText(/current/)).not.toBeInTheDocument();
  });

  it('rejects missing or invalid details without calling the API', async () => {
    const fetchMock = mockApi([]);
    renderWithProviders(<GoalsPage />, '/goals');
    await screen.findByText('You have not set any goals yet.');
    await userEvent.type(screen.getByLabelText('Target value'), '-5');
    await userEvent.click(screen.getByRole('button', { name: 'Save goal' }));
    expect(screen.getByText('Enter a target greater than zero.')).toBeInTheDocument();
    expect(screen.getByText('Choose a date in the future.')).toBeInTheDocument();
    expect(screen.getByText('Goal not saved.')).toBeInTheDocument();
    expect(fetchMock.mock.calls.some(([, i]) => i?.method === 'POST')).toBe(false);
  });

  it('saves a goal, then pauses it', async () => {
    const fetchMock = mockApi([]);
    renderWithProviders(<GoalsPage />, '/goals');
    await screen.findByText('You have not set any goals yet.');
    await userEvent.type(screen.getByLabelText('Target value'), '70');
    await userEvent.type(screen.getByLabelText('Target date'), '2099-01-31');
    await userEvent.click(screen.getByRole('button', { name: 'Save goal' }));
    expect(await screen.findByText('Goal saved.')).toBeInTheDocument();
    const post = fetchMock.mock.calls.find(([, i]) => i?.method === 'POST');
    expect(JSON.parse(String(post?.[1]?.body))).toEqual({
      category: 'weight_management',
      metric_type: 'weight',
      target_value: 70,
      target_unit: 'kg',
      target_date: '2099-01-31',
    });
    const card = await screen.findByRole('article', { name: 'Weight management · Weight to 70 kg' });
    await userEvent.click(within(card).getByRole('button', { name: 'Pause goal' }));
    const paused = await screen.findByText('Paused');
    expect(paused).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Resume goal' })).toBeInTheDocument();
  });
});
