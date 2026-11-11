import { expect, test } from './_pipeline_guard';
import { resetDemoState } from './_reset';

test.beforeEach(() => resetDemoState());

// Seed login: backend/app/seeds/constants.py. asha has 24 days of weight and only 4 days of steps.
const EMAIL = 'asha@sapphire.example';
const PASSWORD = 'Wellness-Demo-2026!';

test('asha creates a goal, sees insufficient then available trends, rates an insight, sees the goal on the dashboard', async ({
  page,
}) => {
  await page.goto('/login');
  await page.getByLabel('Email address').fill(EMAIL);
  await page.getByLabel('Password').fill(PASSWORD);
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page).toHaveURL(/\/dashboard$/);
  const nav = page.getByRole('navigation', { name: 'Primary' });

  await nav.getByRole('link', { name: 'Goals' }).click();
  await page.getByLabel('Goal category').selectOption('weight_management');
  await page.getByLabel('Target value').fill('60');
  await page.getByLabel('Target date').fill('2099-01-31');
  await page.getByRole('button', { name: 'Save goal' }).click();
  await expect(page.getByText('Goal saved.')).toBeVisible();
  await expect(page.getByRole('article', { name: 'Weight management · Weight to 60 kg' }).first()).toBeVisible();

  await nav.getByRole('link', { name: 'Trends' }).click();
  await expect(page.getByRole('heading', { name: 'Trends and insights', level: 1 })).toBeVisible();

  // Too few steps readings in 365 days: explained, not implied.
  await page.getByLabel('Metric', { exact: true }).selectOption('steps');
  await page.getByLabel('365 days', { exact: true }).check();
  await expect(page.getByText('Not enough data to show a trend')).toBeVisible();

  // Weight has enough readings.
  await page.getByLabel('Metric', { exact: true }).selectOption('weight');
  await page.getByLabel('30 days', { exact: true }).check();
  await expect(page.getByRole('heading', { name: 'Weight over the last 30 days' })).toBeVisible();
  await expect(page.getByRole('table').getByRole('columnheader', { name: 'Weight (kg)' })).toBeVisible();
  await expect(page.getByText('Not enough data to show a trend')).toHaveCount(0);

  await expect(page.getByRole('heading', { name: 'What we measured' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Wellness guidance' })).toBeVisible();
  await page.getByRole('button', { name: 'Not useful', exact: true }).click();
  await expect(page.getByText(/Your feedback was saved/)).toBeVisible();
  await expect(page.getByRole('button', { name: 'Not useful', exact: true })).toHaveAttribute('aria-pressed', 'true');

  await nav.getByRole('link', { name: 'Dashboard' }).click();
  const goals = page.getByRole('heading', { name: 'Goal progress' }).locator('..');
  await expect(goals.getByText(/Weight/).first()).toBeVisible();
});
