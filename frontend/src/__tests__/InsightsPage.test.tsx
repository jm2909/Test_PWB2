import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import InsightsPage from '../pages/InsightsPage';
import { AuthProvider } from '../lib/auth-context';
import { storeSession } from '../lib/api-client';

function json(status: number, body: unknown) {
  return Promise.resolve(
    new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } }),
  );
}

interface Data {
  alerts: unknown[];
  insights: unknown[];
  rec: unknown;
}
let data: Data;
let posts: string[];

beforeEach(() => {
  posts = [];
  data = {
    alerts: [
      { id: 'a1', trend_name: 'Resting heart rate has trended up over 14 days', urgency: 'routine', what_we_saw: 'Moved from 62 to 68 bpm.', recommended_next_action: 'Review your sleep.', care_direction: null, created_at: '2026-11-14T00:00:00Z' },
      { id: 'a2', trend_name: 'Sustained change', urgency: 'urgent_direction', what_we_saw: 'Above usual range.', recommended_next_action: 'Check in.', care_direction: 'Contact your doctor or a qualified health professional.', created_at: '2026-11-14T00:00:00Z' },
    ],
    insights: [{ id: 'i1', status: 'published', observed_trend: 'Sleep fell.', wellness_implication: 'Steadier bedtime may help.', suppression_reason: null }],
    rec: { status: 'available', action_text: 'Set a regular bedtime for the next 7 days', reason_text: 'Sleep fell.', insight_id: 'i1', suggested_goal_type: 'sleep_improvement' },
  };
  storeSession({
    access_token: 't',
    expires_at: '2030-01-01T00:00:00Z',
    user: { id: 1, email: 'asha.menon@example.com', onboarding_status: 'complete' },
  });
  vi.stubGlobal(
    'fetch',
    vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (init?.method === 'POST') {
        posts.push(url);
        data.insights = [{ id: 'i2', status: 'suppressed', observed_trend: null, wellness_implication: null, suppression_reason: 'insufficient_evidence' }];
        data.rec = { status: 'none' };
        return json(201, data.insights[0]);
      }
      if (url.includes('/alerts')) return json(200, { items: data.alerts, total: data.alerts.length });
      if (url.includes('/insights')) return json(200, { items: data.insights, total: data.insights.length });
      return json(200, data.rec);
    }),
  );
});
afterEach(() => vi.unstubAllGlobals());

function renderPage() {
  return render(
    <MemoryRouter>
      <AuthProvider>
        <InsightsPage />
      </AuthProvider>
    </MemoryRouter>,
  );
}

describe('InsightsPage', () => {
  it('shows routine and urgent alerts, the insight and the recommendation without a tel link', async () => {
    const { container } = renderPage();
    expect(await screen.findByText('Resting heart rate has trended up over 14 days')).toBeInTheDocument();
    expect(screen.getByText('Needs attention')).toBeInTheDocument();
    expect(screen.getByText('Where to turn')).toBeInTheDocument();
    expect(screen.getByText(/Contact your doctor/)).toBeInTheDocument();
    expect(container.querySelector('a[href^="tel:"]')).toBeNull();
    expect(screen.getByText('Steadier bedtime may help.')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'View the sleep trend' })).toHaveAttribute('href', '/trends');
    expect(screen.getByText('Set a regular bedtime for the next 7 days')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Set a sleep goal/ })).toHaveAttribute('href', '/goals');
  });

  it('shows suppressed and no-recommendation states', async () => {
    data.alerts = [];
    data.insights = [{ id: 'i0', status: 'suppressed', observed_trend: null, wellness_implication: null, suppression_reason: 'insufficient_evidence' }];
    data.rec = { status: 'none' };
    renderPage();
    expect(await screen.findByText("We don't have enough reliable data to give you an insight yet.")).toBeInTheDocument();
    expect(screen.getByText(/No action to suggest right now/)).toBeInTheDocument();
  });

  it('generates an insight and refreshes', async () => {
    const user = userEvent.setup();
    renderPage();
    await screen.findByText('Steadier bedtime may help.');
    await user.click(screen.getByRole('button', { name: 'Generate insight' }));
    expect(await screen.findByText("We don't have enough reliable data to give you an insight yet.")).toBeInTheDocument();
    expect(posts).toHaveLength(1);
    expect(posts[0]).toMatch(/\/insights$/);
  });
});
