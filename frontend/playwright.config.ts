import { defineConfig } from '@playwright/test';

const backendPort = process.env.E2E_BACKEND_PORT ?? '8765';
const frontendPort = process.env.E2E_FRONTEND_PORT ?? '5173';
const py = process.env.E2E_PYTHON ?? 'python';
const databaseUrl = process.env.E2E_DATABASE_URL ?? 'sqlite:///./e2e.db';

export default defineConfig({
  testDir: './e2e',
  globalSetup: './e2e/_global_setup.ts',
  retries: 0,
  workers: 1,
  timeout: Number(process.env.E2E_TEST_TIMEOUT ?? 30_000),
  reporter: [['list']],
  use: {
    baseURL: `http://127.0.0.1:${frontendPort}`,
    actionTimeout: Number(process.env.E2E_ACTION_TIMEOUT ?? 10_000),
    navigationTimeout: Number(process.env.E2E_NAVIGATION_TIMEOUT ?? 15_000),
  },
  webServer: [
    {
      command: `${py} -m alembic upgrade head && ${py} -m app.seed && ${py} -m uvicorn app.main:app --host 127.0.0.1 --port ${backendPort}`,
      cwd: '../backend',
      env: {
        DATABASE_URL: databaseUrl,
        JWT_SECRET_KEY: process.env.JWT_SECRET_KEY ?? 'e2e-only-secret-0123456789abcdef0123456789',
        RATE_LIMIT_ENABLED: 'false',
        CORS_ORIGINS: `http://127.0.0.1:${frontendPort},http://localhost:${frontendPort}`,
      },
      url: `http://127.0.0.1:${backendPort}/health`,
      reuseExistingServer: false,
      timeout: 180_000,
      stdout: 'pipe',
      stderr: 'pipe',
    },
    {
      command: `npm run dev -- --host 127.0.0.1 --port ${frontendPort} --strictPort`,
      env: { BACKEND_PORT: backendPort },
      url: `http://127.0.0.1:${frontendPort}`,
      reuseExistingServer: false,
      timeout: 180_000,
      stdout: 'pipe',
      stderr: 'pipe',
    },
  ],
});
