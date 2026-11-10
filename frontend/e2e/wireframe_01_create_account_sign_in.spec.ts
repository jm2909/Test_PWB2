import { expect, test } from './_pipeline_guard';

test('asha signs in through the form with the seed credentials', async ({ page }) => {
  await page.goto('/login');
  await expect(page.getByRole('tab', { name: 'Sign in', selected: true })).toBeVisible();
  await expect(page.getByLabel('Email address', { exact: true })).toHaveValue('asha.menon@example.com');
  await page.getByLabel('Email address', { exact: true }).fill('asha.menon@example.com');
  await page.getByLabel('Password', { exact: true }).fill('correct-horse-battery');
  await page.getByRole('button', { name: 'Sign in' }).click();

  await expect(page).toHaveURL(/\/$/);
  await expect(page.getByRole('heading', { level: 1, name: /Good (morning|afternoon|evening), Asha/ })).toBeVisible();
});

test('wrong password shows the sign-in failed notice and no health data', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Password', { exact: true }).fill('not-the-password-123');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page.getByRole('alert')).toContainText('Sign-in failed');
  await expect(page.getByRole('alert')).toContainText('Email or password is incorrect.');
  await expect(page).toHaveURL(/\/login$/);
});

test('a new account is created and lands on onboarding', async ({ page }) => {
  const email = `new.user.${Date.now()}@example.com`;
  await page.goto('/register');
  await expect(page.getByRole('heading', { name: 'Create your account' })).toBeVisible();
  await page.getByLabel('Email address', { exact: true }).fill(email);
  await page.getByLabel('Password', { exact: true }).fill('short-pass');
  await page.getByRole('button', { name: /Create account/ }).click();
  await expect(page.getByText('Password must be 12 to 128 characters.')).toBeVisible();

  await page.getByLabel('Password', { exact: true }).fill('a-long-enough-password');
  await page.getByRole('button', { name: /Create account/ }).click();
  await expect(page).toHaveURL(/\/onboarding$/);
  await expect(page.getByRole('heading', { level: 1, name: 'Set up FitConnect' })).toBeVisible();
  await expect(page.getByRole('banner').getByText(email)).toBeVisible();
});

test('registering an existing email shows the inline conflict error', async ({ page, apiGuard }) => {
  apiGuard.allow(409, '/accounts');
  await page.goto('/register');
  await page.getByLabel('Email address', { exact: true }).fill('asha.menon@example.com');
  await page.getByLabel('Password', { exact: true }).fill('correct-horse-battery');
  await page.getByRole('button', { name: /Create account/ }).click();
  await expect(page.getByText(/An account with this email already exists\./)).toBeVisible();
  await expect(page.getByRole('link', { name: 'Sign in instead.' })).toBeVisible();
});
