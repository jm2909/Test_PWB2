import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import RequireAuth from '../components/auth/RequireAuth';
import { AuthProvider } from '../lib/auth-context';
import { storeSession } from '../lib/api-client';

function renderAt(path: string) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<p>login screen</p>} />
          <Route element={<RequireAuth />}>
            <Route path="/trends" element={<p>private data</p>} />
          </Route>
        </Routes>
      </AuthProvider>
    </MemoryRouter>,
  );
}

describe('RequireAuth', () => {
  it('redirects signed-out visitors to /login without rendering protected content', () => {
    renderAt('/trends');
    expect(screen.getByText('login screen')).toBeInTheDocument();
    expect(screen.queryByText('private data')).not.toBeInTheDocument();
  });

  it('renders the protected route for a signed-in user', () => {
    storeSession({
      access_token: 't',
      expires_at: '2030-01-01T00:00:00Z',
      user: { id: 1, email: 'a@example.com', onboarding_status: 'complete' },
    });
    renderAt('/trends');
    expect(screen.getByText('private data')).toBeInTheDocument();
  });
});
