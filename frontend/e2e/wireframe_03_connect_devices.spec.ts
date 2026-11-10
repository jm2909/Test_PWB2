import { expect, test } from './_pipeline_guard';

test('asha reconnects revoked wearable platform C', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email address', { exact: true }).fill('asha.menon@example.com');
  await page.getByLabel('Password', { exact: true }).fill('correct-horse-battery');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page).toHaveURL(/\/$/);

  await page.getByRole('navigation', { name: 'Primary' }).getByRole('link', { name: 'Devices' }).click();
  await expect(page.getByRole('heading', { level: 1, name: 'Devices' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Sapphire smart scale' })).toBeVisible();

  const row = page.getByRole('listitem').filter({ hasText: 'Wearable platform C' });
  await expect(row.getByText('Revoked', { exact: true })).toBeVisible();

  const post = page.waitForResponse(
    (r) => r.url().endsWith('/api/v1/device-connections') && r.request().method() === 'POST',
  );
  await row.getByRole('button', { name: 'Reconnect' }).click();
  const saved = (await (await post).json()) as { status: string; permitted_categories: string[] };
  expect(saved.status).toBe('connected');

  await expect(row.getByText('Connected', { exact: true })).toBeVisible();
  // Chips come from the backend response (platform C permits sleep and activity).
  const labels: Record<string, string> = { sleep: 'Sleep', heart_rate: 'Heart rate', activity: 'Activity' };
  expect(saved.permitted_categories.length).toBeGreaterThan(0);
  for (const c of saved.permitted_categories) {
    await expect(row.getByText(labels[c], { exact: true })).toBeVisible();
  }
  await expect(row.getByText('Sleep', { exact: true })).toBeVisible();
  await expect(row.getByText('Activity', { exact: true })).toBeVisible();
  await expect(row.getByRole('link', { name: 'View sync status' })).toBeVisible();
});
