import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import DashboardPage from '../pages/DashboardPage';
import { AuthProvider } from '../lib/auth-context';
import { storeSession } from '../lib/api-client';

function json(status: number, body: unknown) {
  return Promise.resolve(
    new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } }),
  );
}

function mockDashboard(body: unknown) {
  vi.stubGlobal('fetch', vi.fn(() => json(200, body)));
}

beforeEach(() => {
  storeSession({
    access_token: 't',
    expires_at: '2030-01-01T00:00:00Z',
    user: { id: 1, email: 'asha.menon@example.com', onboarding_status: 'complete' },
  });
});

function renderPage() {
  return render(
    <MemoryRouter>
      <AuthProvider>
        <DashboardPage />
      </AuthProvider>
    </MemoryRouter>,
  );
}

describe('DashboardPage', () => {
  it('renders tiles, the alert banner and links', async () => {
    mockDashboard({
      display_name: 'Asha',
      last_synced_at: null,
      unread_alert_count: 1,
      signal_groups: [
        { key: 'body_composition', title: 'Body composition', value: '68.4', unit: 'kg', details: ['Body fat 24.1%'] },
        { key: 'goals', title: 'Goal', value: '68.4', unit: 'kg', details: ['Target 65 kg'] },
      ],
      source_gaps: [],
      active_goals: [],
    });
    renderPage();
    expect(await screen.findByRole('heading', { level: 1, name: /Asha/ })).toBeInTheDocument();
    expect(screen.getByText('You have 1 new wellness alert')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Read the alert/ })).toHaveAttribute('href', '/insights');
    expect(screen.getByRole('heading', { name: 'Goal signals' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /View trend/ })).toHaveAttribute('href', '/trends');
    expect(screen.getByRole('link', { name: /Review goal/ })).toHaveAttribute('href', '/goals');
  });

  it('shows gaps as dashed tiles without blocking other tiles', async () => {
    mockDashboard({
      display_name: 'Meena',
      last_synced_at: null,
      unread_alert_count: 0,
      signal_groups: [{ key: 'activity', title: 'Activity', value: '8,420', unit: 'steps today', details: [] }],
      source_gaps: [
        {
          key: 'sleep',
          title: 'Sleep',
          reason: 'Your wearable has not synced sleep readings.',
          recovery_action: 'Check wearable connection',
          link: '/devices',
        },
        { key: 'goals', title: 'Goals', reason: 'No goal set', recovery_action: 'Set a goal', link: '/goals' },
      ],
      active_goals: [],
    });
    renderPage();
    expect(await screen.findByText('No sleep data yet')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Check wearable connection/ })).toHaveAttribute('href', '/devices/sync');
    expect(screen.getByText('No goal set')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Set a goal/ })).toHaveAttribute('href', '/goals');
    expect(screen.getByText('8,420')).toBeInTheDocument();
    expect(screen.queryByText(/new wellness alert/)).not.toBeInTheDocument();
  });
});
