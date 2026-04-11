import axios from 'axios'
import { getAccessToken, getAdminApiKey, getApiBaseUrl } from './storage'

export const api = axios.create({
  baseURL: getApiBaseUrl(),
})

api.interceptors.request.use((config) => {
  // Always refresh baseURL from Settings/localStorage
  config.baseURL = getApiBaseUrl()

  if (config.url?.startsWith('/api/v1/admin/')) {
    const key = getAdminApiKey()
    if (key) {
      config.headers = config.headers || {}
      config.headers['X-API-Key'] = key
    }
  }

  const token = getAccessToken()
  if (token) {
    config.headers = config.headers || {}
    if (!config.headers.Authorization) {
      config.headers.Authorization = `Bearer ${token}`
    }
  }
  return config
})

