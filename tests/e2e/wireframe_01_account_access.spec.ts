import { expect, test } from './_pipeline_guard';

// Seed login: backend/app/seeds/constants.py (asha).
const SEED_EMAIL = 'asha@sapphire.example';
const SEED_PASSWORD = 'Wellness-Demo-2026!';

test('register a fresh user, land on consent, sign out, sign in with the seed login', async ({ page }) => {
  const email = `fresh-${Date.now()}@example.com`;
  await page.goto('/register');
  await page.getByLabel('Display name').fill('Fresh User');
  await page.getByLabel('Email address').fill(email);
  await page.getByLabel('Password').fill('a-long-enough-password');
  await page.getByRole('button', { name: 'Create account' }).click();

  await expect(page).toHaveURL(/\/consent$/);
  await expect(page.getByRole('heading', { name: 'Privacy consent and data rights' })).toBeVisible();
  await expect(page.getByText('No consent recorded.')).toBeVisible();

  await page.getByRole('banner').getByRole('button', { name: 'Sign out' }).click();
  await expect(page).toHaveURL(/\/login$/);
  await expect(page.getByText('You have signed out.')).toBeVisible();

  await page.getByLabel('Email address').fill(SEED_EMAIL);
  await page.getByLabel('Password').fill(SEED_PASSWORD);
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page).toHaveURL(/\/dashboard$/);
  await expect(page.getByRole('banner').getByText('Signed in as Asha')).toBeVisible();
});
