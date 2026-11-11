import { expect, test } from './_pipeline_guard';
import { resetDemoState } from './_reset';

test.beforeEach(() => resetDemoState());

// Seed login: backend/app/seeds/constants.py. asha has active alerts.
const EMAIL = 'asha@sapphire.example';
const PASSWORD = 'Wellness-Demo-2026!';

test('asha acknowledges an alert, sees it on the dashboard, and opens support from it', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email address').fill(EMAIL);
  await page.getByLabel('Password').fill(PASSWORD);
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page).toHaveURL(/\/dashboard$/);

  await page.getByRole('navigation', { name: 'Primary' }).getByRole('link', { name: 'Alerts' }).click();
  await expect(page.getByRole('heading', { name: 'Alerts', level: 1 })).toBeVisible();

  const active = page.getByRole('region', { name: 'Active alerts' });
  const card = active.getByRole('article').first();
  const title = (await card.getByRole('heading').first().textContent()) ?? '';
  await card.getByRole('button', { name: 'Acknowledge alert' }).click();
  await expect(page.getByText('Alert acknowledged.')).toBeVisible();

  const history = page.getByRole('region', { name: 'Acknowledged alerts and history' });
  const moved = history.getByRole('article', { name: title.trim() }).first();
  await expect(moved).toBeVisible();

  // Dashboard distinguishes acknowledged from active alerts.
  await page.getByRole('navigation', { name: 'Primary' }).getByRole('link', { name: 'Dashboard' }).click();
  await expect(page.getByRole('heading', { name: 'Your wellness dashboard', level: 1 })).toBeVisible();
  await expect(page.locator('li[data-state="acknowledged"]').first()).toBeVisible();

  // Support from an alert context, ending with a reference.
  await page.getByRole('navigation', { name: 'Primary' }).getByRole('link', { name: 'Alerts' }).click();
  const supportLink = page
    .getByRole('region', { name: 'Acknowledged alerts and history' })
    .getByRole('link', { name: /support/i })
    .first();
  await supportLink.click();
  await expect(page).toHaveURL(/\/support\?context=alert&id=/);
  await expect(page.getByLabel(/An alert/)).toBeChecked();
  await page.getByLabel('Describe the problem').fill('I would like help understanding this alert.');
  await page.getByRole('button', { name: 'Send request' }).click();
  await expect(page.getByText('Request received.')).toBeVisible();
  await expect(page.getByText(/SUP-[0-9A-F]{16}/i)).toBeVisible();
});
