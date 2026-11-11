import { loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import { configDefaults, defineConfig } from 'vitest/config';

export default defineConfig(({ mode }) => {
  // '' loads every variable, including the process environment start.sh sets.
  const env = loadEnv(mode, process.cwd(), '');
  const backend = `http://127.0.0.1:${env.BACKEND_PORT || 9000}`;
  return {
    plugins: [react()],
    server: {
      port: 5173,
      // No rewrite: the backend mounts its routes under /api, so the path passes unchanged.
      proxy: { '/api': { target: backend } },
    },
    preview: { proxy: { '/api': { target: backend } } },
    test: {
      environment: 'jsdom',
      globals: true,
      setupFiles: ['./src/test/setup.ts'],
      include: ['src/**/*.{test,spec}.{ts,tsx}'],
      exclude: [...configDefaults.exclude, 'e2e/**'],
    },
  };
});
