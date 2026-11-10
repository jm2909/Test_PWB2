import { expect, test, type Page } from './_pipeline_guard';

async function login(page: Page, email: string, password: string) {
  await page.goto('/login');
  await page.getByLabel('Email address', { exact: true }).fill(email);
  await page.getByLabel('Password', { exact: true }).fill(password);
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page).not.toHaveURL(/\/login$/);
  await page.goto('/');
}

test('asha sees body composition and goal signals', async ({ page }) => {
  await login(page, 'asha.menon@example.com', 'correct-horse-battery');
  await expect(page.getByRole('heading', { level: 1, name: /^Good (morning|afternoon|evening), / })).toBeVisible();
  const body = page.locator('section', { has: page.getByRole('heading', { name: 'Body composition' }) });
  await expect(body.getByText('68.4')).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Goal signals' })).toBeVisible();
  await expect(page.getByRole('link', { name: /Review goal/ })).toBeVisible();
});

test('rohan (no sleep readings) sees the sleep gap and follows it to sync status', async ({ page }) => {
  await login(page, 'rohan.iyer@example.com', 'correct-horse-battery');
  await expect(page.getByText('No sleep data yet')).toBeVisible();
  await expect(page.getByText('No goal set')).toBeVisible();
  const sleep = page.locator('section', { has: page.getByRole('heading', { name: 'Sleep' }) });
  await sleep.getByRole('link', { name: /Check wearable connection/ }).click();
  await expect(page).toHaveURL(/\/devices\/sync$/);
  await expect(page.getByRole('heading', { level: 1, name: 'Sync status' })).toBeVisible();
});
