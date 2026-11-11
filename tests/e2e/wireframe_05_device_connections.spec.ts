import { expect, test } from './_pipeline_guard';

// Seed login: backend/app/seeds/constants.py. asha has consent, a stale Bedroom scale and a failed wearable.
const EMAIL = 'asha@sapphire.example';
const PASSWORD = 'Wellness-Demo-2026!';

test('asha sees seeded stale and failed cards and connects a new scale', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email address').fill(EMAIL);
  await page.getByLabel('Password').fill(PASSWORD);
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page).toHaveURL(/\/dashboard$/);

  await page.getByRole('navigation', { name: 'Primary' }).getByRole('link', { name: 'Connections' }).click();
  await expect(page.getByRole('heading', { name: 'Device connections', level: 1 })).toBeVisible();

  const stale = page.getByRole('article', { name: 'Sapphire Smart Scale – Bedroom' });
  await expect(stale.getByText('Stale')).toBeVisible();
  await expect(stale.getByText(/\d{1,2} \w{3} \d{4}, \d{2}:\d{2}/)).toBeVisible();
  await expect(stale.getByRole('button', { name: 'Retry sync' })).toBeVisible();
  await expect(stale.getByRole('link', { name: 'Contact support' })).toBeVisible();

  const failed = page.getByRole('article', { name: 'Provider B' });
  await expect(failed.getByText('Failed')).toBeVisible();
  await expect(failed.getByText(/Connection could not be completed/)).toBeVisible();
  await expect(failed.getByRole('button', { name: 'Retry' })).toBeVisible();

  await page.getByLabel('Choose your scale').selectOption('SSC-0733');
  await page.getByRole('button', { name: 'Connect scale' }).click();
  const added = page.getByRole('article', { name: 'Sapphire Smart Scale – Living room' });
  await expect(added).toBeVisible();
  await expect(added.getByText('Connected', { exact: true })).toBeVisible();
});
