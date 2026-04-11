import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const msprRoot = path.resolve(__dirname, '..')

/** FastAPI expose /health, /docs, etc. à la racine — sans proxy, Vite renvoie index.html. */
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, msprRoot, ['VITE_', 'API_'])
  const explicit = (process.env.VITE_API_PROXY_TARGET || env.VITE_API_PROXY_TARGET || '').trim()
  // Port sur l’hôte (navigateur), pas forcément API_PORT du .env (souvent le port interne uvicorn / conteneur).
  const port = (env.VITE_PUBLIC_API_PORT || '8001').trim()
  const apiTarget = explicit || `http://127.0.0.1:${port}`
  const toApi = { target: apiTarget, changeOrigin: true as const }

  return {
    envDir: msprRoot,
    plugins: [react()],
    server: {
      port: 5173,
      proxy: {
        '/api': toApi,
        '/health': toApi,
        '/docs': toApi,
        '/redoc': toApi,
        '/openapi.json': toApi,
      },
    },
  }
})
