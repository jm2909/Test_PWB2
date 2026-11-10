import { expect, test, type Page } from './_pipeline_guard';

async function login(page: Page, email: string, password: string) {
  await page.goto('/login');
  await page.getByLabel('Email address', { exact: true }).fill(email);
  await page.getByLabel('Password', { exact: true }).fill(password);
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page).not.toHaveURL(/\/login$/);
}

test('asha reviews weight, then sees the empty and unavailable states', async ({ page }) => {
  await login(page, 'asha.menon@example.com', 'correct-horse-battery');
  const first = page.waitForResponse(
    (r) => r.url().includes('/metric-explanations') && r.request().method() === 'POST',
  );
  await page.getByRole('navigation', { name: 'Primary' }).getByRole('link', { name: 'Trends' }).click();
  await expect(page.getByRole('heading', { level: 1, name: 'Trends' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Weight over the last 30 days' })).toBeVisible();
  const body = (await (await first).json()) as { explanation: string };
  expect(body.explanation.length).toBeGreaterThan(10);
  await expect(page.getByRole('complementary').getByText(body.explanation)).toBeVisible();
  await expect(page.getByRole('img', { name: /Line chart of weight/ })).toBeVisible();
  await expect(page.getByRole('table')).toBeVisible();
  await page.getByRole('button', { name: 'Hide table view' }).click();
  await expect(page.getByRole('table')).toHaveCount(0);

  await page.getByRole('button', { name: '365 days' }).click();
  await expect(page.getByText('A reliable trend is not available yet.')).toBeVisible();
  await expect(page.getByRole('link', { name: 'Check sync status' })).toBeVisible();

  await page.getByLabel('Metric').selectOption({ label: 'Body fat' });
  await page.getByRole('button', { name: '7 days' }).click();
  await expect(page.getByText("We can't explain this metric yet.")).toBeVisible();
});
