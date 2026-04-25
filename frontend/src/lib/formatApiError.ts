import axios from 'axios'
import { getApiBaseUrl } from './storage'

function fastApiDetail(data: unknown): string | null {
  if (!data || typeof data !== 'object') return null
  const d = data as { detail?: unknown }
  if (typeof d.detail === 'string') return d.detail
  if (Array.isArray(d.detail)) {
    const parts = d.detail.map((x: unknown) => {
      if (x && typeof x === 'object' && 'msg' in x) return String((x as { msg: string }).msg)
      return JSON.stringify(x)
    })
    return parts.join(' ; ')
  }
  return null
}

/** Human-readable message for failed API calls (axios or unknown). */
export function formatApiError(err: unknown, fallback: string): string {
  const base = getApiBaseUrl() || '(même origine — proxy /api en dev)'

  if (axios.isAxiosError(err)) {
    if (err.code === 'ERR_NETWORK' || err.message === 'Network Error') {
      return `Aucune réponse du serveur. API configurée : ${base}. Vérifie que l’API tourne, le bon port (Docker hôte souvent 8001, voir VITE_PUBLIC_API_PORT dans mspr/.env), puis redémarre npm run dev.`
    }
    const status = err.response?.status
    if (status === 404) {
      return `Route introuvable (404). L’URL ${base} ne sert peut‑être pas cette API.`
    }
    if (status === 0 || err.message?.toLowerCase().includes('cors')) {
      return `Blocage CORS ou réseau. URL : ${base}.`
    }
    if (status != null && status >= 400) {
      const detail = fastApiDetail(err.response?.data)
      if (detail) {
        return `Erreur ${status} : ${detail} (URL : ${base})`
      }
      if (status >= 500) {
        return `Erreur serveur (${status}). Souvent MySQL arrêté ou migrations non appliquées. URL : ${base}.`
      }
    }
  }

  return fallback
}
