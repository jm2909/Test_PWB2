import { expect, test } from './_pipeline_guard';
import { resetDemoState } from './_reset';

test.beforeEach(() => resetDemoState());

// Seed logins: backend/app/seeds/constants.py. asha has a weight reading, a stale Bedroom scale and an active alert;
// rohan has no readings, connections or alerts.
const PASSWORD = 'Wellness-Demo-2026!';

async function login(page: import('./_pipeline_guard').Page, email: string) {
  await page.goto('/login');
  await page.getByLabel('Email address').fill(email);
  await page.getByLabel('Password').fill(PASSWORD);
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page).toHaveURL(/\/dashboard$/);
}

test('asha sees the seeded weight tile, a stale source and an active alert', async ({ page }) => {
  await login(page, 'asha@sapphire.example');
  await expect(page.getByRole('heading', { name: 'Your wellness dashboard', level: 1 })).toBeVisible();

  const weight = page.getByRole('article', { name: 'Weight' });
  await expect(weight.getByText('68.4')).toBeVisible();
  await expect(weight.getByText('Sapphire scale')).toBeVisible();

  const table = page.getByRole('table');
  const bedroom = table.getByRole('row', { name: /Bedroom/ });
  await expect(bedroom.getByText('Stale')).toBeVisible();

  const active = page.locator('li[data-state="active"]').first();
  await expect(active.getByText('Active')).toBeVisible();
  await expect(active.getByRole('link', { name: 'View details and acknowledge' })).toBeVisible();
  await expect(page.locator('li[data-state="acknowledged"]').first()).toBeVisible();
});

test('rohan sees explicit unavailable states', async ({ page }) => {
  await login(page, 'rohan@sapphire.example');
  for (const name of ['Weight', 'Steps', 'Sleep', 'Active time']) {
    await expect(page.getByRole('article', { name }).getByText('Unavailable')).toBeVisible();
  }
  await expect(page.getByText('No sources are connected yet.')).toBeVisible();
  await expect(page.getByText('No alerts right now.')).toBeVisible();
});
