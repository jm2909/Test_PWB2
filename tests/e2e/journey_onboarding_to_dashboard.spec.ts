import { expect, test } from './_pipeline_guard';

// Journey: register -> consent -> connect scale -> dashboard shows the source. Uses a fresh account per run.
test('new user registers, consents, connects a scale and sees it on the dashboard', async ({ page }) => {
  const email = `onboard-${Date.now()}@example.com`;
  const password = 'Onboarding-Pass-2026!';

  await page.goto('/register');
  await page.getByLabel('Display name').fill('Onboard User');
  await page.getByLabel('Email address').fill(email);
  await page.getByLabel('Password').fill(password);
  await page.getByRole('button', { name: 'Create account' }).click();

  // Registration signs the user in and leads to consent setup.
  await expect(page).toHaveURL(/\/consent$/);
  await expect(page.getByRole('heading', { name: 'Privacy consent and data rights' })).toBeVisible();

  await page.getByLabel(/I agree to the collection/).check();
  await page.getByRole('button', { name: 'Save my decision' }).click();
  await expect(page.getByText('Consent granted', { exact: true })).toBeVisible();

  await page.getByRole('navigation', { name: 'Primary' }).getByRole('link', { name: 'Connections' }).click();
  await expect(page.getByRole('heading', { name: 'Device connections', level: 1 })).toBeVisible();
  await page.getByLabel('Choose your scale').selectOption('SSC-0733');
  await page.getByRole('button', { name: 'Connect scale' }).click();
  const added = page.getByRole('article', { name: 'Sapphire Smart Scale – Living room' });
  await expect(added).toBeVisible();
  await expect(added.getByText('Connected', { exact: true })).toBeVisible();

  await page.getByRole('navigation', { name: 'Primary' }).getByRole('link', { name: 'Dashboard' }).click();
  await expect(page.getByRole('heading', { name: 'Your wellness dashboard', level: 1 })).toBeVisible();
  const table = page.getByRole('table');
  await expect(table.getByRole('row', { name: /Living room/ })).toBeVisible();
  // No reading yet: the category is shown as unavailable, never as a value.
  await expect(page.getByRole('article', { name: 'Weight' }).getByText('Unavailable')).toBeVisible();
});
