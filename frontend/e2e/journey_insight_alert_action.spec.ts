import { expect, test, type Page } from './_pipeline_guard';

const FOOTER =
  'FitConnect shares wellness information, not medical advice. It cannot diagnose conditions or respond to emergencies.';

async function expectFooter(page: Page) {
  await expect(page.locator('footer').filter({ hasText: FOOTER }).first()).toBeVisible();
}

test('insight and alert: sign in -> dashboard alert banner -> insights -> recommendation -> sleep goal -> dashboard', async ({
  page,
}) => {
  await page.goto('/login');
  await page.getByLabel('Email address', { exact: true }).fill('asha.menon@example.com');
  await page.getByLabel('Password', { exact: true }).fill('correct-horse-battery');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page).toHaveURL(/\/$/);

  // Alerts are materialized when listed, so visit insights once, then the banner is on the dashboard.
  const nav = page.getByRole('navigation', { name: 'Primary' });
  await nav.getByRole('link', { name: 'Insights and alerts' }).click();
  await expect(page.getByRole('heading', { level: 1, name: 'Insights and alerts' })).toBeVisible();
  await expect(page.getByTestId('alert-routine')).toBeVisible();
  await nav.getByRole('link', { name: 'Dashboard' }).click();
  await expect(page.getByRole('heading', { level: 1, name: /^Good (morning|afternoon|evening), / })).toBeVisible();
  const banner = page.getByText(/You have \d+ new wellness alerts?/);
  await expect(banner).toBeVisible();
  await expectFooter(page);

  await page.getByRole('link', { name: 'Read the alert and suggested next step' }).click();
  await expect(page).toHaveURL(/\/insights$/);
  await expectFooter(page);

  const urgent = page.getByTestId('alert-urgent');
  await expect(urgent).toContainText('Needs attention');
  await expect(urgent).toContainText('qualified health professional');
  await expect(page.locator('a[href^="tel:"]')).toHaveCount(0);
  await expect(page.getByTestId('alert-routine')).toContainText('Suggested next step');

  const insight = page.getByTestId('insight-published');
  await expect(insight).toContainText('Observed trend');
  await expect(insight).toContainText('Wellness implication');
  await expect(page.getByTestId('recommendation')).toContainText('Why');

  await page.getByRole('link', { name: /Set a sleep goal/ }).click();
  await expect(page).toHaveURL(/\/goals$/);
  await expectFooter(page);
  await page.getByRole('radio', { name: /Sleep improvement/ }).check();
  await page.getByLabel('Target value').fill('8');
  await page.getByRole('button', { name: /Save goal/ }).click();
  await expect(page.getByText('Goal saved and active.')).toBeVisible();
  await expect(page.getByTestId('active-goal').filter({ hasText: 'Sleep improvement' })).toBeVisible();

  await nav.getByRole('link', { name: 'Dashboard' }).click();
  const goalTile = page.locator('section', { has: page.getByRole('heading', { name: 'Goal signals' }) });
  await expect(goalTile).toBeVisible();
  await expectFooter(page);
});
