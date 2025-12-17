const DEFAULT_API_PATH = '/api/v1'

const trimTrailingSlashes = (value: string): string => value.replace(/\/+$/, '')

export function getApiBaseUrl(): string {
  const envUrl = (import.meta.env.VITE_API_URL as string | undefined)?.trim()
  if (envUrl) {
    return trimTrailingSlashes(envUrl)
  }

  const port = import.meta.env.VITE_BACKEND_PORT || '8003'
  const protocol =
    (import.meta.env.VITE_BACKEND_PROTOCOL as string | undefined)?.trim() ||
    (typeof window !== 'undefined' && window.location.protocol
      ? window.location.protocol.replace(':', '')
      : 'http')

  if (import.meta.env.DEV) {
    return `${protocol}://localhost:${port}${DEFAULT_API_PATH}`
  }

  if (typeof window !== 'undefined' && window.location.origin) {
    return `${window.location.origin}${DEFAULT_API_PATH}`
  }

  return DEFAULT_API_PATH
}

export function getBackendBaseUrl(): string {
  const apiBase = getApiBaseUrl()

  if (apiBase.startsWith('http')) {
    const url = new URL(apiBase)
    const pathWithoutApi = url.pathname.replace(/\/api\/v1$/, '')
    return trimTrailingSlashes(`${url.origin}${pathWithoutApi}`)
  }

  return trimTrailingSlashes(apiBase.replace(/\/api\/v1$/, ''))
}
