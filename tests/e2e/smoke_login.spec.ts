import { expect, test } from './_pipeline_guard';

// Seed credentials: backend/app/seeds/constants.py (asha).
const EMAIL = 'asha@sapphire.example';
const PASSWORD = 'Wellness-Demo-2026!';

test('asha signs in through the form and the header shows her name', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email address').fill(EMAIL);
  await page.getByLabel('Password').fill(PASSWORD);
  await page.getByRole('button', { name: 'Sign in' }).click();

  const header = page.getByRole('banner');
  await expect(header.getByText('Signed in as Asha')).toBeVisible();
  await expect(header.getByRole('button', { name: 'Sign out' })).toBeVisible();
  await expect(page).toHaveURL(/\/dashboard$/);
});
