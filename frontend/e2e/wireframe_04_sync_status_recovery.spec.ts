import { expect, test } from './_pipeline_guard';
import { resetDatabase } from './_reset_db';

test.beforeEach(() => {
  resetDatabase();
});

test('asha retries failed wearable platform B and sees the backend summary', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email address', { exact: true }).fill('asha.menon@example.com');
  await page.getByLabel('Password', { exact: true }).fill('correct-horse-battery');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page).toHaveURL(/\/$/);

  await page.goto('/devices/sync');
  await expect(page.getByRole('heading', { level: 1, name: 'Sync status' })).toBeVisible();
  const table = page.getByRole('table');
  const row = table.getByRole('row').filter({ hasText: 'Wearable platform B' });
  await expect(row.getByText('Failed', { exact: true })).toBeVisible();
  await expect(row.getByText('The provider did not respond.')).toBeVisible();

  const post = page.waitForResponse((r) => r.url().endsWith('/api/v1/sync') && r.request().method() === 'POST');
  await row.getByRole('button', { name: /Retry/ }).click();
  const res = await post;
  expect(res.status()).toBe(200);
  expect(res.request().headers()['idempotency-key'].length).toBeGreaterThanOrEqual(16);
  const body = (await res.json()) as { status: string; last_sync_summary: { new_readings: number } };
  expect(body.status).toBe('connected');
  const n = body.last_sync_summary.new_readings;

  await expect(page.getByText(`Sync complete. ${n} new readings added.`)).toBeVisible();
  await expect(page.getByTestId('added-count')).toHaveText(String(n));
  await expect(row.getByText('Connected', { exact: true })).toBeVisible();
});
