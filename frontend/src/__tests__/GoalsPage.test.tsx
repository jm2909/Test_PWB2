import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import GoalsPage from '../pages/GoalsPage';
import { AuthProvider } from '../lib/auth-context';
import { storeSession } from '../lib/api-client';

function json(status: number, body: unknown) {
  return Promise.resolve(
    new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } }),
  );
}

let goals: Record<string, unknown>[];
let posts: Record<string, unknown>[];

beforeEach(() => {
  goals = [{ id: 'g1', goal_type: 'weight_loss', target_value: 65, target_unit: 'kg', status: 'active' }];
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
      if (url.endsWith('/goals') && init?.method === 'POST') {
        const body = JSON.parse(String(init.body)) as Record<string, unknown>;
        posts.push(body);
        if (Number(body.target_value) <= 0) {
          return json(422, {
            detail: 'Enter a target above 0 kg that is realistic for you, for example 65.',
          });
        }
        const g = { id: 'g2', status: 'active', ...body };
        goals = [g];
        return json(201, g);
      }
      return json(200, { items: goals, total: goals.length });
    }),
  );
});
afterEach(() => vi.unstubAllGlobals());

function renderPage() {
  return render(
    <MemoryRouter>
      <AuthProvider>
        <GoalsPage />
      </AuthProvider>
    </MemoryRouter>,
  );
}

describe('GoalsPage', () => {
  it('shows the form and the active goal', async () => {
    renderPage();
    expect(screen.getByRole('heading', { level: 1, name: 'Goals' })).toBeInTheDocument();
    expect(screen.getByRole('radio', { name: /Blood-pressure control/ })).toBeInTheDocument();
    expect(await screen.findByTestId('active-goal')).toHaveTextContent('65');
    expect(screen.getByText('Goals are for everyday wellness')).toBeInTheDocument();
  });

  it('saves a sleep goal and shows the active tile', async () => {
    renderPage();
    await userEvent.click(screen.getByRole('radio', { name: /Sleep improvement/ }));
    const value = screen.getByLabelText('Target value');
    await userEvent.clear(value);
    await userEvent.type(value, '8');
    expect(screen.getByLabelText('Unit')).toHaveValue('h');
    await userEvent.click(screen.getByRole('button', { name: /Save goal/ }));
    expect(await screen.findByText('Goal saved and active.')).toBeInTheDocument();
    expect(posts[0]).toEqual({ goal_type: 'sleep_improvement', target_value: 8, target_unit: 'h' });
    expect(await screen.findByText('Sleep improvement', { selector: 'p' })).toBeInTheDocument();
  });

  it('shows the 422 guidance as a field error and an alert', async () => {
    renderPage();
    const value = screen.getByLabelText('Target value');
    await userEvent.clear(value);
    await userEvent.type(value, '-5');
    await userEvent.click(screen.getByRole('button', { name: /Save goal/ }));
    expect(
      await screen.findByText('Enter a target above 0 kg that is realistic for you, for example 65.'),
    ).toBeInTheDocument();
    expect(screen.getByRole('alert')).toHaveTextContent('Goal not saved');
    expect(value).toHaveAttribute('aria-invalid', 'true');
    expect(screen.queryByText('Goal saved and active.')).not.toBeInTheDocument();
  });
});
