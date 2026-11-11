import { expect, test } from './_pipeline_guard';
import { resetDemoState } from './_reset';

test.beforeEach(() => resetDemoState());

const EMAIL = 'asha@sapphire.example';
const PASSWORD = 'Wellness-Demo-2026!';

test('asha views the 30-day weight trend and saves Useful feedback', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email address').fill(EMAIL);
  await page.getByLabel('Password').fill(PASSWORD);
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page).toHaveURL(/\/dashboard$/);

  await page.getByRole('navigation', { name: 'Primary' }).getByRole('link', { name: 'Trends' }).click();
  await expect(page.getByRole('heading', { name: 'Trends and insights', level: 1 })).toBeVisible();

  await page.getByLabel('Metric', { exact: true }).selectOption('weight');
  await page.getByLabel('30 days', { exact: true }).check();
  await expect(page.getByRole('heading', { name: 'Weight over the last 30 days' })).toBeVisible();

  const table = page.getByRole('table');
  await expect(table.getByRole('columnheader', { name: 'Weight (kg)' })).toBeVisible();
  await expect(table.getByRole('columnheader', { name: 'Source' })).toBeVisible();
  await expect(table.getByRole('row')).not.toHaveCount(1);
  await expect(table.getByText('Sapphire scale').first()).toBeVisible();

  await expect(page.getByRole('heading', { name: 'What we measured' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Wellness guidance' })).toBeVisible();
  await page.getByRole('button', { name: 'Useful', exact: true }).click();
  await expect(page.getByText(/Your feedback was saved/)).toBeVisible();
  await expect(page.getByRole('button', { name: 'Useful', exact: true })).toHaveAttribute('aria-pressed', 'true');
});
