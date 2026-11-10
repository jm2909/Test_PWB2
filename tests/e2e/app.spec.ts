import { expect, test } from './_pipeline_guard';
import type { Page } from './_pipeline_guard';

const EMAIL = 'asha.menon@example.com';
const PASSWORD = 'correct-horse-battery';

async function loginViaForm(page: Page) {
  await page.goto('/login');
  await page.getByLabel('Email address', { exact: true }).fill(EMAIL);
  await page.getByLabel('Password', { exact: true }).fill(PASSWORD);
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page).not.toHaveURL(/\/login/);
}

const nav = (page: Page) => page.getByRole('navigation', { name: 'Primary' });

test('login through the form lands on the dashboard', async ({ page }) => {
  await loginViaForm(page);
  await expect(page).toHaveURL(/\/$/);
  await expect(
    page.getByRole('heading', { level: 1, name: /^Good (morning|afternoon|evening), / }),
  ).toBeVisible();
  await expect(page.getByRole('banner').getByText(EMAIL)).toBeVisible();
});

test('wrong password shows an error and stays on login', async ({ page, apiGuard }) => {
  apiGuard.allow(401, '/auth/sessions');
  await page.goto('/login');
  await page.getByLabel('Email address', { exact: true }).fill(EMAIL);
  await page.getByLabel('Password', { exact: true }).fill('not-the-password');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page.getByRole('alert')).toContainText('Email or password is incorrect.');
  await expect(page).toHaveURL(/\/login$/);
});

test('every protected route renders its heading and data', async ({ page }) => {
  await loginViaForm(page);

  await page.goto('/');
  await expect(page.getByRole('heading', { level: 1, name: /^Good / })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Sleep' })).toBeVisible();

  await page.goto('/devices');
  await expect(page.getByRole('heading', { level: 1, name: 'Devices' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Sapphire smart scale' })).toBeVisible();
  await expect(page.getByRole('listitem').filter({ hasText: 'Wearable platform A' })).toBeVisible();

  await page.goto('/devices/sync');
  await expect(page.getByRole('heading', { level: 1, name: 'Sync status' })).toBeVisible();
  await expect(page.getByRole('row', { name: 'Wearable platform A Connected' })).toBeVisible();

  await page.goto('/trends');
  await expect(page.getByRole('heading', { level: 1, name: 'Trends' })).toBeVisible();
  await expect(page.getByRole('img', { name: /Line chart of/ })).toBeVisible();

  await page.goto('/insights');
  await expect(page.getByRole('heading', { level: 1, name: 'Insights and alerts' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Insight', exact: true })).toBeVisible();

  await page.goto('/goals');
  await expect(page.getByRole('heading', { level: 1, name: 'Goals' })).toBeVisible();
  await expect(page.getByTestId('active-goal')).toBeVisible();
});

test('onboarding route renders for a signed-in user', async ({ page }) => {
  await loginViaForm(page);
  await page.goto('/onboarding');
  await expect(page.getByRole('heading', { level: 1, name: 'Set up FitConnect' })).toBeVisible();
});

test('registration creates an account and lands on onboarding', async ({ page }) => {
  const email = `e2e.user.${Date.now()}@example.com`;
  await page.goto('/register');
  await expect(page.getByRole('heading', { name: 'Create your account' })).toBeVisible();
  await page.getByLabel('Email address', { exact: true }).fill(email);
  await page.getByLabel('Password', { exact: true }).fill('a-long-enough-password');
  await page.getByRole('button', { name: /Create account/ }).click();
  await expect(page).toHaveURL(/\/onboarding$/);
  await expect(page.getByRole('heading', { level: 1, name: 'Set up FitConnect' })).toBeVisible();
  await expect(page.getByRole('banner').getByText(email)).toBeVisible();
});

test('saving a goal shows it as the active goal', async ({ page }) => {
  await loginViaForm(page);
  await nav(page).getByRole('link', { name: 'Goals' }).click();
  await expect(page.getByRole('heading', { level: 1, name: 'Goals' })).toBeVisible();
  await page.getByRole('radio', { name: /Sleep improvement/ }).check();
  await page.getByLabel('Target value').fill('8');
  await page.getByRole('button', { name: /Save goal/ }).click();
  await expect(page.getByText('Goal saved and active.')).toBeVisible();
  const tile = page.getByTestId('active-goal').filter({ hasText: 'Sleep improvement' });
  await expect(tile).toBeVisible();
  await expect(tile).toContainText('8');
});

test('sync retry on a failed connection finishes connected', async ({ page }) => {
  await loginViaForm(page);
  await nav(page).getByRole('link', { name: 'Devices' }).click();
  await page.getByRole('listitem').filter({ hasText: 'Wearable platform A' }).getByRole('link', { name: 'View sync status' }).click();
  await expect(page.getByRole('heading', { level: 1, name: 'Sync status' })).toBeVisible();
  const row = page.getByRole('table').getByRole('row').filter({ hasText: 'Wearable platform B' });
  await expect(row.getByText('Failed', { exact: true })).toBeVisible();
  const post = page.waitForResponse((r) => r.url().endsWith('/api/v1/sync') && r.request().method() === 'POST');
  await row.getByRole('button', { name: /Retry|Try again/ }).click();
  const res = await post;
  expect(res.status()).toBe(200);
  const body = (await res.json()) as { status: string };
  expect(body.status).toBe('connected');
  await expect(page.getByText('Sync complete.', { exact: false }).first()).toBeVisible();
  await expect(row.getByText('Connected', { exact: true })).toBeVisible();
});

test('logout returns to login and protects routes', async ({ page }) => {
  await loginViaForm(page);
  await page.getByRole('button', { name: 'Sign out' }).click();
  await expect(page).toHaveURL(/\/login$/);
  await page.goto('/goals');
  await expect(page).toHaveURL(/\/login/);
});
