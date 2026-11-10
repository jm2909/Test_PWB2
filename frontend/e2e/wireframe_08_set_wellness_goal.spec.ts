import { expect, test } from './_pipeline_guard';
import { resetDatabase } from './_reset_db';

test.beforeEach(() => {
  resetDatabase();
});

test('asha saves a sleep goal and sees the correction for an invalid target', async ({ page, apiGuard }) => {
  apiGuard.allow(422, '/goals');
  await page.goto('/login');
  await page.getByLabel('Email address', { exact: true }).fill('asha.menon@example.com');
  await page.getByLabel('Password', { exact: true }).fill('correct-horse-battery');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page).toHaveURL(/\/$/);

  await page.getByRole('navigation', { name: 'Primary' }).getByRole('link', { name: 'Goals' }).click();
  await expect(page.getByRole('heading', { level: 1, name: 'Goals' })).toBeVisible();
  await expect(page.getByTestId('active-goal')).toContainText('Weight loss');

  await page.getByRole('radio', { name: /Sleep improvement/ }).check();
  await page.getByLabel('Target value').fill('8');
  await page.getByRole('button', { name: /Save goal/ }).click();
  await expect(page.getByText('Goal saved and active.')).toBeVisible();
  const tile = page.getByTestId('active-goal').filter({ hasText: 'Sleep improvement' });
  await expect(tile).toContainText('8');
  await expect(tile).toContainText('h');

  await page.getByRole('radio', { name: /Weight loss/ }).check();
  await page.getByLabel('Target value').fill('-5');
  await page.getByRole('button', { name: /Save goal/ }).click();
  await expect(page.getByText('Enter a target above 0 kg that is realistic for you, for example 65.')).toBeVisible();
  await expect(page.getByRole('alert').filter({ hasText: 'Goal not saved' })).toBeVisible();
  await expect(page.getByText('Goal saved and active.')).toHaveCount(0);
});
