import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import TrendsPage from '../pages/TrendsPage';
import { AuthProvider } from '../lib/auth-context';
import { storeSession } from '../lib/api-client';

function json(status: number, body: unknown) {
  return Promise.resolve(
    new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } }),
  );
}

const pts = [
  { observed_at: '2026-10-15T08:00:00Z', value: 70.1 },
  { observed_at: '2026-10-25T08:00:00Z', value: 69.5 },
  { observed_at: '2026-11-14T08:00:00Z', value: 68.4 },
];

let urls: string[];
let posts: unknown[];

beforeEach(() => {
  urls = [];
  posts = [];
  storeSession({
    access_token: 't',
    expires_at: '2030-01-01T00:00:00Z',
    user: { id: 1, email: 'asha.menon@example.com', onboarding_status: 'complete' },
  });
  vi.stubGlobal(
    'fetch',
    vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      urls.push(url);
      if (init?.method === 'POST') {
        const body = JSON.parse(String(init.body)) as { metric_type: string; period_days: number };
        posts.push(body);
        if (body.metric_type === 'body_fat')
          return json(200, {
            status: 'unavailable', direction: null, reading_count: 3, source_label: 'Smart scale',
            explanation: "We can't explain this metric yet. We would rather not guess.",
          });
        if (body.period_days === 365)
          return json(200, {
            status: 'insufficient_history', direction: null, reading_count: 1, source_label: 'Smart scale',
            explanation: 'A reliable trend is not available yet.',
          });
        return json(200, {
          status: 'available', direction: 'down', reading_count: 3, source_label: 'Smart scale',
          explanation: 'Your weight has gone down gradually.',
        });
      }
      const params = new URL(url, 'http://x').searchParams;
      if (params.get('period_days') === '365')
        return json(200, { metric_type: 'weight', period_days: 365, status: 'insufficient_history', points: pts.slice(0, 1), explanation: 'x', reading_count: 1, source_label: 'Smart scale' });
      return json(200, { metric_type: params.get('metric_type'), period_days: 30, status: 'available', points: pts, explanation: 'x', reading_count: 3, source_label: 'Smart scale' });
    }),
  );
});
afterEach(() => vi.unstubAllGlobals());

function renderPage() {
  return render(
    <MemoryRouter>
      <AuthProvider>
        <TrendsPage />
      </AuthProvider>
    </MemoryRouter>,
  );
}

describe('TrendsPage', () => {
  it('shows chart, table and the explanation, and toggles the table', async () => {
    const user = userEvent.setup();
    renderPage();
    expect(await screen.findByRole('heading', { name: 'Weight over the last 30 days' })).toBeInTheDocument();
    expect(await screen.findByText('Your weight has gone down gradually.')).toBeInTheDocument();
    expect(screen.getByText('Based on 3 readings from smart scale.')).toBeInTheDocument();
    expect(screen.getByRole('img')).toBeInTheDocument();
    const toggle = screen.getByRole('button', { name: 'Hide table view' });
    expect(toggle).toHaveAttribute('aria-expanded', 'true');
    expect(within(screen.getByRole('table')).getAllByRole('row')).toHaveLength(4);
    await user.click(toggle);
    expect(screen.queryByRole('table')).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Show table view' })).toHaveAttribute('aria-expanded', 'false');
  });

  it('requests a new trend and explanation when the period changes', async () => {
    const user = userEvent.setup();
    renderPage();
    await screen.findByText('Your weight has gone down gradually.');
    await user.click(screen.getByRole('button', { name: '365 days' }));
    expect(await screen.findByText('A reliable trend is not available yet.')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Check sync status' })).toHaveAttribute('href', '/devices/sync');
    expect(posts).toContainEqual({ metric_type: 'weight', period_days: 365 });
    expect(screen.getByRole('button', { name: '365 days' })).toHaveAttribute('aria-pressed', 'true');
  });

  it('says it cannot explain body fat but still shows readings', async () => {
    const user = userEvent.setup();
    renderPage();
    await screen.findByText('Your weight has gone down gradually.');
    await user.selectOptions(screen.getByLabelText('Metric'), 'body_fat');
    expect(await screen.findByText(/We can't explain this metric yet/)).toBeInTheDocument();
    expect(await screen.findByRole('table')).toBeInTheDocument();
  });
});
