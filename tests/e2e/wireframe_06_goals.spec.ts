import { expect, test } from './_pipeline_guard';

// Seed login: backend/app/seeds/constants.py. asha already has weight, sleep, steps and active-minutes goals.
const EMAIL = 'asha@sapphire.example';
const PASSWORD = 'Wellness-Demo-2026!';

test('asha creates a goal, sees its card, and pauses it', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email address').fill(EMAIL);
  await page.getByLabel('Password').fill(PASSWORD);
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page).toHaveURL(/\/dashboard$/);

  await page.getByRole('navigation', { name: 'Primary' }).getByRole('link', { name: 'Goals' }).click();
  await expect(page.getByRole('heading', { name: 'Goals', level: 1 })).toBeVisible();

  await page.getByLabel('Goal category').selectOption('weight_management');
  await page.getByLabel('Target value').fill('-5');
  await page.getByRole('button', { name: 'Save goal' }).click();
  await expect(page.getByText('Enter a target greater than zero.')).toBeVisible();

  await page.getByLabel('Target value').fill('61');
  await page.getByLabel('Target date').fill('2099-01-31');
  await page.getByRole('button', { name: 'Save goal' }).click();
  await expect(page.getByText('Goal saved.')).toBeVisible();

  const card = page.getByRole('article', { name: 'Weight management · Weight to 61 kg' });
  await expect(card).toBeVisible();
  await expect(card.getByText('Active', { exact: true })).toBeVisible();

  await card.getByRole('button', { name: 'Pause goal' }).click();
  await expect(card.getByText('Paused', { exact: true })).toBeVisible();
  await expect(card.getByRole('button', { name: 'Resume goal' })).toBeVisible();
});
