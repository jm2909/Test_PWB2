import { expect, test, type Page } from './_pipeline_guard';

const FOOTER =
  'FitConnect shares wellness information, not medical advice. It cannot diagnose conditions or respond to emergencies.';

async function expectFooter(page: Page) {
  await expect(page.locator('footer').filter({ hasText: FOOTER }).first()).toBeVisible();
}

test('sync recovery: devices -> sync status -> retry failed provider -> dashboard -> trend -> explanation', async ({
  page,
}) => {
  await page.goto('/login');
  await expectFooter(page);
  await page.getByLabel('Email address', { exact: true }).fill('asha.menon@example.com');
  await page.getByLabel('Password', { exact: true }).fill('correct-horse-battery');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page).toHaveURL(/\/$/);

  const nav = page.getByRole('navigation', { name: 'Primary' });
  await nav.getByRole('link', { name: 'Devices' }).click();
  await expect(page.getByRole('heading', { level: 1, name: 'Devices' })).toBeVisible();
  await expectFooter(page);
  await page.getByRole('listitem').filter({ hasText: 'Wearable platform A' }).getByRole('link', { name: 'View sync status' }).click();

  await expect(page.getByRole('heading', { level: 1, name: 'Sync status' })).toBeVisible();
  await expectFooter(page);
  const row = page.getByRole('table').getByRole('row').filter({ hasText: 'Wearable platform B' });
  await expect(row.getByText('Failed', { exact: true })).toBeVisible();
  await expect(row.getByText('The provider did not respond.')).toBeVisible();
  // A revoked connection is never shown as current.
  const revoked = page.getByRole('table').getByRole('row').filter({ hasText: 'Wearable platform C' });
  await expect(revoked.getByText('Revoked', { exact: true })).toBeVisible();

  const post = page.waitForResponse((r) => r.url().endsWith('/api/v1/sync') && r.request().method() === 'POST');
  await row.getByRole('button', { name: /Retry|Try again/ }).click();
  const res = await post;
  expect(res.status()).toBe(200);
  const body = (await res.json()) as { status: string; last_sync_summary: { new_readings: number } };
  expect(body.status).toBe('connected');
  await expect(page.getByText(`Sync complete. ${body.last_sync_summary.new_readings} new readings added.`)).toBeVisible();
  await expect(row.getByText('Connected', { exact: true })).toBeVisible();

  await nav.getByRole('link', { name: 'Dashboard' }).click();
  await expect(page.getByRole('heading', { level: 1, name: /^Good (morning|afternoon|evening), / })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Sleep' })).toBeVisible();
  await expect(page.getByText('No sleep data yet')).toHaveCount(0);
  await expectFooter(page);

  await nav.getByRole('link', { name: 'Trends' }).click();
  await expect(page.getByRole('heading', { level: 1, name: 'Trends' })).toBeVisible();
  await expectFooter(page);
  await expect(page.getByRole('heading', { name: 'Weight over the last 30 days' })).toBeVisible();
  await expect(page.getByRole('img', { name: /Line chart of weight/ })).toBeVisible();
  await expect(page.getByRole('complementary').getByText(/Based on \d+ readings/)).toBeVisible();
  await page.getByRole('button', { name: '365 days' }).click();
  await expect(page.getByText('A reliable trend is not available yet.')).toBeVisible();
});
