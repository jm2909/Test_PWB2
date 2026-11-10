import { execFileSync } from 'node:child_process';
import path from 'node:path';

/** Restore the E2E database to its seeded state so specs that mutate shared data stay independent. */
export function resetDatabase(): void {
  const py = process.env.E2E_PYTHON ?? 'python';
  const frontendPort = process.env.E2E_FRONTEND_PORT ?? '5173';
  execFileSync(py, ['-m', 'scripts.e2e_reset'], {
    cwd: path.resolve(process.cwd(), '../backend'),
    env: {
      ...process.env,
      DATABASE_URL: process.env.E2E_DATABASE_URL ?? 'sqlite:///./e2e.db',
      JWT_SECRET_KEY: process.env.JWT_SECRET_KEY ?? 'e2e-only-secret-0123456789abcdef0123456789',
      RATE_LIMIT_ENABLED: 'false',
      CORS_ORIGINS: `http://127.0.0.1:${frontendPort},http://localhost:${frontendPort}`,
    },
    stdio: 'pipe',
  });
}
