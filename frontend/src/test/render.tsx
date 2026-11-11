import type { ReactElement } from 'react';
import { render } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { AuthProvider } from '../lib/auth-context';

/** The one render helper: wraps pages in the providers the app really uses. */
export function renderWithProviders(ui: ReactElement, route: string | { pathname: string; state?: unknown } = '/') {
  return render(
    <MemoryRouter initialEntries={[route]}>
      <AuthProvider>{ui}</AuthProvider>
    </MemoryRouter>,
  );
}
