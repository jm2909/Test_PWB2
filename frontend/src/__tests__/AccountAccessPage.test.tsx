import { screen } from '@testing-library/react';
import { Route, Routes } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import { AccountAccessPage } from '../pages/AccountAccessPage';
import { renderWithProviders } from '../test/render';

describe('AccountAccessPage', () => {
  it('shows the register and sign-in forms together', () => {
    renderWithProviders(
      <Routes>
        <Route path="/account" element={<AccountAccessPage />} />
      </Routes>,
      '/account',
    );
    expect(screen.getByRole('heading', { name: 'Account access' })).toBeInTheDocument();
    expect(screen.getByRole('form', { name: 'Create your account' })).toBeInTheDocument();
    expect(screen.getByRole('form', { name: 'Sign in' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Create account' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Sign in' })).toBeInTheDocument();
  });
});
