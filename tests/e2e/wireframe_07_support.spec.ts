import { expect, test } from './_pipeline_guard';

const EMAIL = 'asha@sapphire.example';
const PASSWORD = 'Wellness-Demo-2026!';

test('asha opens support from a failed connection, submits and sees a reference', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email address').fill(EMAIL);
  await page.getByLabel('Password').fill(PASSWORD);
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page).toHaveURL(/\/dashboard$/);

  await page.getByRole('navigation', { name: 'Primary' }).getByRole('link', { name: 'Connections' }).click();
  const failed = page.getByRole('article', { name: 'Provider B' });
  await expect(failed.getByText('Failed')).toBeVisible();
  await failed.getByRole('link', { name: 'Contact support' }).click();

  await expect(page).toHaveURL(/\/support\?context=device&id=/);
  await expect(page.getByRole('heading', { name: 'Contact support', level: 1 })).toBeVisible();
  await expect(page.getByLabel(/A device connection/)).toBeChecked();
  await expect(page.getByLabel('Category')).toHaveValue('connection');

  await page.getByLabel('Describe the problem').fill('My wearable keeps saying the connection could not be completed.');
  await page.getByRole('button', { name: 'Send request' }).click();

  await expect(page.getByText('Request received.')).toBeVisible();
  await expect(page.getByText(/SUP-[0-9A-F]{16}/i)).toBeVisible();
  await expect(page.locator('dt:has-text("Status") + dd')).toHaveText('Submitted');
});
