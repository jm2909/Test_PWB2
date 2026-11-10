import { expect, test, type Page } from './_pipeline_guard';

async function login(page: Page, email: string, password: string) {
  await page.goto('/login');
  await page.getByLabel('Email address', { exact: true }).fill(email);
  await page.getByLabel('Password', { exact: true }).fill(password);
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page).not.toHaveURL(/\/login$/);
}

async function openInsights(page: Page) {
  await page.getByRole('navigation', { name: 'Primary' }).getByRole('link', { name: 'Insights and alerts' }).click();
  await expect(page.getByRole('heading', { level: 1, name: 'Insights and alerts' })).toBeVisible();
}

test('asha sees alerts, a published insight and a recommendation, then goes to goals', async ({ page }) => {
  await login(page, 'asha.menon@example.com', 'correct-horse-battery');
  await openInsights(page);

  await expect(page.getByTestId('alert-routine')).toContainText('Routine');
  await expect(page.getByTestId('alert-routine')).toContainText('Suggested next step');
  const urgent = page.getByTestId('alert-urgent');
  await expect(urgent).toContainText('Needs attention');
  await expect(urgent).toContainText('Where to turn');
  await expect(urgent).toContainText('qualified health professional');
  await expect(page.locator('a[href^="tel:"]')).toHaveCount(0);

  const insight = page.getByTestId('insight-published');
  await expect(insight).toContainText('Observed trend');
  await expect(insight).toContainText('Wellness implication');
  await expect(page.getByTestId('recommendation')).toContainText('Set a regular bedtime for the next 7 days');

  await page.getByRole('link', { name: /Set a sleep goal/ }).click();
  await expect(page).toHaveURL(/\/goals$/);
  await expect(page.getByRole('heading', { level: 1, name: 'Goals' })).toBeVisible();
});

test('meena sees the suppressed insight and no recommendation', async ({ page }) => {
  await login(page, 'meena.rao@example.com', 'correct-horse-battery');
  await page.goto('/insights');
  await expect(page.getByRole('heading', { level: 1, name: 'Insights and alerts' })).toBeVisible();
  await expect(page.getByText("We don't have enough reliable data to give you an insight yet.")).toBeVisible();
  await expect(page.getByText('No action to suggest right now.')).toBeVisible();
  await expect(page.getByTestId('insight-published')).toHaveCount(0);
});
