import react from '@vitejs/plugin-react';
import { defineConfig, loadEnv } from 'vite';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  const backendPort = process.env.BACKEND_PORT ?? env.BACKEND_PORT ?? '9000';
  const target = `http://localhost:${backendPort}`;
  return {
    plugins: [react()],
    server: {
      port: 5173,
      proxy: { '/api': { target, changeOrigin: true } },
    },
    preview: {
      proxy: { '/api': { target, changeOrigin: true } },
    },
  };
});
