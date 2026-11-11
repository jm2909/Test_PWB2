import { expect, test } from './_pipeline_guard';
import { resetDemoState } from './_reset';

test.beforeEach(() => resetDemoState());

// Seed login: backend/app/seeds/constants.py. asha has two active alerts and one acknowledged alert.
const EMAIL = 'asha@sapphire.example';
const PASSWORD = 'Wellness-Demo-2026!';

test('asha acknowledges an active alert and sees it in the acknowledged list with a time', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email address').fill(EMAIL);
  await page.getByLabel('Password').fill(PASSWORD);
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page).toHaveURL(/\/dashboard$/);

  await page.getByRole('navigation', { name: 'Primary' }).getByRole('link', { name: 'Alerts' }).click();
  await expect(page.getByRole('heading', { name: 'Alerts', level: 1 })).toBeVisible();

  const active = page.getByRole('region', { name: 'Active alerts' });
  const card = active.getByRole('article', { name: 'Weight change pattern' });
  await expect(card.getByText(/weight-change-pattern · version/)).toBeVisible();
  await card.getByRole('button', { name: 'Acknowledge alert' }).click();

  await expect(page.getByText('Alert acknowledged.')).toBeVisible();
  await expect(active.getByRole('article', { name: 'Weight change pattern' })).toHaveCount(0);

  const history = page.getByRole('region', { name: 'Acknowledged alerts and history' });
  const moved = history.getByRole('article', { name: 'Weight change pattern' });
  await expect(moved).toBeVisible();
  await expect(moved.getByText('Acknowledged', { exact: true }).first()).toBeVisible();
  await expect(moved.locator('dt:has-text("Acknowledged") + dd')).toHaveText(/\d{1,2} \w{3} \d{4}, \d{2}:\d{2}/);
});
