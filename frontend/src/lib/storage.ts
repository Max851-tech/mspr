const KEYS = {
  apiBaseUrl: 'healthai.apiBaseUrl',
  adminApiKey: 'healthai.adminApiKey',
  accessToken: 'healthai.accessToken',
} as const

function defaultApiBaseUrl(): string {
  const fromEnv = import.meta.env.VITE_API_BASE_URL as string | undefined
  if (fromEnv && fromEnv.trim()) {
    return fromEnv.trim()
  }
  // Dev: requêtes relatives → proxy Vite /api → backend (vite.config.ts)
  if (import.meta.env.DEV) {
    return ''
  }
  return 'http://localhost:8001'
}

export function getApiBaseUrl(): string {
  const saved = localStorage.getItem(KEYS.apiBaseUrl)
  if (saved !== null) {
    return saved
  }
  return defaultApiBaseUrl()
}

export function setApiBaseUrl(url: string) {
  localStorage.setItem(KEYS.apiBaseUrl, url)
}

export function getAdminApiKey(): string {
  return localStorage.getItem(KEYS.adminApiKey) || ''
}

export function setAdminApiKey(key: string) {
  localStorage.setItem(KEYS.adminApiKey, key)
}

export function getAccessToken(): string {
  return localStorage.getItem(KEYS.accessToken) || ''
}

export function setAccessToken(token: string) {
  localStorage.setItem(KEYS.accessToken, token)
}

export function clearAccessToken() {
  localStorage.removeItem(KEYS.accessToken)
}

