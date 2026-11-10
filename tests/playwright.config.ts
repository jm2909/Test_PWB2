import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  retries: 0,
  workers: 1,
  timeout: 45_000,
  use: {
    baseURL: process.env.E2E_BASE_URL ?? 'http://127.0.0.1:5200',
    actionTimeout: 10_000,
    navigationTimeout: 15_000,
  },
});
