import { useState } from 'react'
import { Button, Card, Input, Label, PageHeader } from '../components/ui'
import {
  clearAccessToken,
  getAccessToken,
  getAdminApiKey,
  getApiBaseUrl,
  setAdminApiKey,
  setApiBaseUrl,
  setAccessToken,
} from '../lib/storage'

export function SettingsPage() {
  const [apiBaseUrl, setApiBaseUrlState] = useState(getApiBaseUrl())
  const [adminApiKey, setAdminApiKeyState] = useState(getAdminApiKey())
  const [accessToken, setAccessTokenState] = useState(getAccessToken())
  const [saved, setSaved] = useState<string | null>(null)

  return (
    <div>
      <PageHeader title="Settings" subtitle="Configuration locale (stockée dans ton navigateur)." />

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card>
          <div className="space-y-2">
            <Label>API Base URL</Label>
            <Input
              value={apiBaseUrl}
              onChange={(e) => setApiBaseUrlState(e.target.value)}
              placeholder="(vide en dev = proxy Vite → API)"
            />
            <p className="text-xs text-zinc-500">
              En dev, laisse <span className="font-mono">vide</span> pour envoyer les appels vers le même port que Vite (proxy{' '}
              <span className="font-mono">/api</span> → API). Sinon ex. Docker :{' '}
              <span className="font-mono">http://localhost:8001</span>.
            </p>
          </div>
        </Card>

        <Card>
          <div className="space-y-2">
            <Label>Admin API Key (X-API-Key)</Label>
            <Input value={adminApiKey} onChange={(e) => setAdminApiKeyState(e.target.value)} placeholder="dev-admin-key" />
            <p className="text-xs text-zinc-500">Requis pour accéder à <span className="font-mono">/api/v1/admin/*</span>.</p>
          </div>
        </Card>

        <Card className="lg:col-span-2">
          <div className="space-y-2">
            <Label>JWT (Bearer) — stocké localement après login</Label>
            <Input
              value={accessToken}
              onChange={(e) => setAccessTokenState(e.target.value)}
              placeholder="(vide) — utilise la page Login"
            />
            <p className="text-xs text-zinc-500">
              Utilisé automatiquement sur les requêtes API via <span className="font-mono">Authorization: Bearer …</span>.
            </p>
            <div className="pt-2">
              <Button
                variant="ghost"
                type="button"
                onClick={() => {
                  clearAccessToken()
                  setAccessTokenState('')
                }}
              >
                Clear JWT
              </Button>
            </div>
          </div>
        </Card>
      </div>

      <div className="mt-4 flex items-center gap-3">
        <Button
          onClick={() => {
            setApiBaseUrl(apiBaseUrl.trim())
            setAdminApiKey(adminApiKey.trim())
            if (accessToken.trim()) {
              setAccessToken(accessToken.trim())
            } else {
              clearAccessToken()
            }
            setAccessTokenState(getAccessToken())
            setSaved('Enregistré.')
            setTimeout(() => setSaved(null), 1500)
          }}
        >
          Save
        </Button>
        {saved ? <span className="text-sm text-zinc-300">{saved}</span> : null}
      </div>
    </div>
  )
}

