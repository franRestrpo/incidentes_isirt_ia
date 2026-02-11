import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, '', '')
  const apiBaseUrl = env.VITE_API_BASE_URL || 'http://localhost:8081'

  return {
    plugins: [react()],
    server: {
      host: '0.0.0.0',
      allowedHosts: true,
      port: 5173,
      cors: true,
      hmr: false, // Disable HMR in Docker environment
      proxy: {
        '/api/v1': {
          target: apiBaseUrl,
          changeOrigin: true,
          secure: false,
          rewrite: (path) => path.replace(/^\/api\/v1/, '')
        }
      }
    }
  }
})
