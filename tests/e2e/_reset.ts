import { execFileSync } from 'node:child_process';
import path from 'node:path';

/** Restore asha's alerts and insight feedback to the seeded state so specs do not consume each other's data. */
export function resetDemoState(): void {
  const backend = path.resolve(__dirname, '../../backend');
  execFileSync(process.env.E2E_PYTHON ?? 'python', [path.resolve(__dirname, 'reset_demo_state.py')], {
    cwd: backend,
    env: {
      ...process.env,
      PYTHONPATH: backend,
      DATABASE_URL: process.env.E2E_DATABASE_URL ?? 'sqlite:///./e2e.db',
    },
    stdio: 'pipe',
  });
}
