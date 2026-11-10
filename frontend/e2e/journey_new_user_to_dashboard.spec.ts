import { expect, test, type Page } from './_pipeline_guard';

const FOOTER =
  'FitConnect shares wellness information, not medical advice. It cannot diagnose conditions or respond to emergencies.';

async function expectFooter(page: Page) {
  await expect(page.locator('footer').filter({ hasText: FOOTER }).first()).toBeVisible();
}

test('new user: account -> onboarding and consent -> pair scale -> sync -> dashboard weight -> goal', async ({
  page,
}) => {
  const email = `journey.${Date.now()}@example.com`;

  // Create account
  await page.goto('/register');
  await expectFooter(page);
  await page.getByLabel('Email address', { exact: true }).fill(email);
  await page.getByLabel('Password', { exact: true }).fill('journey-pass-phrase-1');
  await page.getByRole('button', { name: /Create account/ }).click();

  // Onboarding and consent
  await expect(page).toHaveURL(/\/onboarding$/);
  await expect(page.getByRole('heading', { level: 1, name: 'Set up FitConnect' })).toBeVisible();
  await expectFooter(page);
  await page.getByLabel('Connect my Sapphire smart scale').check();
  await page.getByLabel('Lose weight').check();
  await page.getByLabel('Display name').fill('Journey');
  await page.getByLabel('Display name').blur();
  const device = page.getByRole('group', { name: 'Device data processing' });
  await device.getByLabel('Accept').click();
  await expect(device.getByText(/Recorded .*policy v1\.0/)).toBeVisible();
  const insights = page.getByRole('group', { name: 'Personalized insights' });
  await insights.getByLabel('Accept').click();
  await expect(insights.getByText(/Recorded .*policy v1\.0/)).toBeVisible();
  await expect(page.getByText(/All required steps are complete/)).toBeVisible();
  await page.getByRole('button', { name: 'Save and finish setup' }).click();
  await expect(page).toHaveURL(/\/$/);
  await expectFooter(page);

  // Devices: pair scale
  const nav = page.getByRole('navigation', { name: 'Primary' });
  await nav.getByRole('link', { name: 'Devices' }).click();
  await expect(page.getByRole('heading', { level: 1, name: 'Devices' })).toBeVisible();
  await expectFooter(page);
  await page.getByRole('button', { name: /Pair scale/ }).click();
  await expect(page.getByText('Connected', { exact: true }).first()).toBeVisible();

  // Sync
  await nav.getByRole('link', { name: 'Devices' }).click();
  await page.goto('/devices/sync');
  await expect(page.getByRole('heading', { level: 1, name: 'Sync status' })).toBeVisible();
  await expectFooter(page);
  const post = page.waitForResponse((r) => r.url().endsWith('/api/v1/sync') && r.request().method() === 'POST');
  await page.getByRole('table').getByRole('button', { name: /Sync now/ }).first().click();
  const res = await post;
  expect(res.status()).toBe(200);
  const body = (await res.json()) as { last_sync_summary: { new_readings: number } };
  expect(body.last_sync_summary.new_readings).toBeGreaterThan(0);
  await expect(page.getByText(`Sync complete. ${body.last_sync_summary.new_readings} new readings added.`)).toBeVisible();

  // Dashboard weight tile
  await nav.getByRole('link', { name: 'Dashboard' }).click();
  await expect(page.getByRole('heading', { level: 1, name: /^Good (morning|afternoon|evening), / })).toBeVisible();
  const bodyTile = page.locator('section', { has: page.getByRole('heading', { name: 'Body composition' }) });
  await expect(bodyTile).toBeVisible();
  await expect(bodyTile.getByText(/kg/).first()).toBeVisible();
  await expect(page.getByText('No goal set')).toBeVisible();
  await expectFooter(page);

  // Goal
  await nav.getByRole('link', { name: 'Goals' }).click();
  await expect(page.getByRole('heading', { level: 1, name: 'Goals' })).toBeVisible();
  await expectFooter(page);
  await page.getByRole('radio', { name: /Weight loss/ }).check();
  await page.getByLabel('Target value').fill('70');
  await page.getByRole('button', { name: /Save goal/ }).click();
  await expect(page.getByText('Goal saved and active.')).toBeVisible();
  await nav.getByRole('link', { name: 'Dashboard' }).click();
  await expect(page.getByRole('heading', { name: 'Goal signals' })).toBeVisible();
  await expect(page.getByText('No goal set')).toHaveCount(0);
});
