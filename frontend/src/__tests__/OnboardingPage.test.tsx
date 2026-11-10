import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import OnboardingPage from '../pages/OnboardingPage';
import { AuthProvider } from '../lib/auth-context';
import { storeSession } from '../lib/api-client';

function json(status: number, body: unknown) {
  return Promise.resolve(
    new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } }),
  );
}

let remaining: string[];
let consents: Record<string, unknown>[];
let calls: { method: string; url: string; body: unknown }[];

beforeEach(() => {
  remaining = ['consent'];
  consents = [];
  calls = [];
  storeSession({
    access_token: 't',
    expires_at: '2030-01-01T00:00:00Z',
    user: { id: 2, email: 'rohan.iyer@example.com', onboarding_status: 'in_progress' },
  });
  vi.stubGlobal(
    'fetch',
    vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      const method = init?.method ?? 'GET';
      const body = init?.body ? JSON.parse(String(init.body)) : undefined;
      calls.push({ method, url, body });
      if (url.endsWith('/consents') && method === 'POST') {
        const rec = { id: 'c' + consents.length, ...body, recorded_at: '2026-11-14T12:00:00Z' };
        consents.push(rec);
        if (consents.length === 2) remaining = [];
        return json(201, rec);
      }
      if (url.endsWith('/consents')) return json(200, { items: consents, total: consents.length, latest: consents });
      return json(200, {
        profile: { display_name: 'Rohan' },
        goal_intent: 'build_muscle',
        device_next_step: 'wearable',
        status: remaining.length ? 'in_progress' : 'complete',
        remaining_steps: remaining,
      });
    }),
  );
});
afterEach(() => vi.unstubAllGlobals());

function renderPage() {
  return render(
    <MemoryRouter>
      <AuthProvider>
        <OnboardingPage />
      </AuthProvider>
    </MemoryRouter>,
  );
}

describe('OnboardingPage', () => {
  it('resumes from saved data and names the remaining step', async () => {
    renderPage();
    expect(await screen.findByText(/You have 1 required step left: Consent/)).toBeInTheDocument();
    expect(screen.getByLabelText('Display name')).toHaveValue('Rohan');
    expect(screen.getByLabelText('Build muscle')).toBeChecked();
    expect(screen.getByLabelText('Connect a smartwatch or wearable')).toBeChecked();
    expect(screen.getByRole('navigation', { name: 'Setup progress' })).toBeInTheDocument();
    expect(screen.getByText('If you decline device data processing')).toBeInTheDocument();
  });

  it('persists a goal choice with PUT /onboarding', async () => {
    renderPage();
    await userEvent.click(await screen.findByLabelText('Sleep better'));
    const put = calls.find((c) => c.method === 'PUT');
    expect(put?.url).toContain('/onboarding');
    expect(put?.body).toMatchObject({ goal_intent: 'sleep_better', device_next_step: 'wearable' });
  });

  it('records each consent with POST /consents and explains declined insights', async () => {
    renderPage();
    const device = await screen.findByRole('group', { name: 'Device data processing' });
    await userEvent.click(within(device).getByLabelText('Accept'));
    const insights = screen.getByRole('group', { name: 'Personalized insights' });
    await userEvent.click(within(insights).getByLabelText('Decline'));
    expect(await screen.findByText('Insights will stay off')).toBeInTheDocument();
    const posts = calls.filter((c) => c.method === 'POST').map((c) => c.body);
    expect(posts).toEqual([
      { purpose: 'device_processing', version: '1.0', status: 'accepted' },
      { purpose: 'personalized_insights', version: '1.0', status: 'declined' },
    ]);
    expect(within(device).getByText(/Recorded .*policy v1\.0/)).toBeInTheDocument();
    expect(await screen.findByText(/All required steps are complete/)).toBeInTheDocument();
  });
});
