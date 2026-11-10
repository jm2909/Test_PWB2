import { expect, test } from './_pipeline_guard';

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

test('rohan resumes setup and records his consent choices', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email address', { exact: true }).fill('rohan.iyer@example.com');
  await page.getByLabel('Password', { exact: true }).fill('correct-horse-battery');
  await page.getByRole('button', { name: 'Sign in' }).click();

  await expect(page).toHaveURL(/\/onboarding$/);
  await expect(page.getByRole('heading', { level: 1, name: 'Set up FitConnect' })).toBeVisible();
  await expect(page.getByText('You have 1 required step left: Consent')).toBeVisible();
  await expect(page.getByRole('banner').getByText('rohan.iyer@example.com')).toBeVisible();

  const device = page.getByRole('group', { name: 'Device data processing' });
  const deviceResponse = page.waitForResponse(
    (r) => r.url().endsWith('/api/v1/consents') && r.request().method() === 'POST',
  );
  await device.getByLabel('Accept').click();
  const recorded = (await (await deviceResponse).json()) as { recorded_at: string; status: string };
  expect(recorded.status).toBe('accepted');
  const d = new Date(recorded.recorded_at);
  const expected = `Recorded ${d.getDate()} ${MONTHS[d.getMonth()]} ${d.getFullYear()}, policy v1.0`;
  await expect(device.getByText(expected)).toBeVisible();

  const insights = page.getByRole('group', { name: 'Personalized insights' });
  await insights.getByLabel('Accept').click();
  await insights.getByLabel('Decline').click();
  await expect(page.getByText('Insights will stay off')).toBeVisible();
  await expect(insights.getByText(/Recorded .*policy v1\.0/)).toBeVisible();
  await expect(page.getByText(/All required steps are complete/)).toBeVisible();

  await page.getByRole('button', { name: 'Save and finish setup' }).click();
  await expect(page).toHaveURL(/\/$/);
});
