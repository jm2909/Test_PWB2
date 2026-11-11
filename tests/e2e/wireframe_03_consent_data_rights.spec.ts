import { expect, test } from './_pipeline_guard';

// Seed login: backend/app/seeds/constants.py (rohan has no consent recorded).
const EMAIL = 'rohan@sapphire.example';
const PASSWORD = 'Wellness-Demo-2026!';

test('rohan grants consent and submits an export request that is listed', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email address').fill(EMAIL);
  await page.getByLabel('Password').fill(PASSWORD);
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page).toHaveURL(/\/dashboard$/);

  await page.getByRole('navigation', { name: 'Primary' }).getByRole('link', { name: 'Privacy and data rights' }).click();
  await expect(page.getByRole('heading', { name: 'Privacy consent and data rights' })).toBeVisible();

  await page.getByLabel(/I agree to the collection/).check();
  await page.getByRole('button', { name: 'Save my decision' }).click();
  await expect(page.getByText('Consent granted', { exact: true })).toBeVisible();

  await page.getByLabel(/Export my data/).check();
  await page.getByRole('button', { name: 'Submit request' }).click();
  await expect(page.getByText('Request received. Keep this reference.')).toBeVisible();

  const reference = (await page.locator('dt:has-text("Reference") + dd').textContent()) ?? '';
  expect(reference).toMatch(/^DR-[0-9A-F]{16}$/i);
  const table = page.getByRole('table', { name: 'Your requests' });
  await expect(table.getByText(reference)).toBeVisible();
});
