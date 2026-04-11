import { useEffect, useState } from 'react'
import { api } from '../lib/api'
import { getApiBaseUrl } from '../lib/storage'
import { Card, PageHeader } from '../components/ui'

export function DashboardPage() {
  const [health, setHealth] = useState<string>('…')
  const baseUrl = getApiBaseUrl()

  useEffect(() => {
    let mounted = true
    api
      .get('/health')
      .then((r) => {
        if (!mounted) return
        const data = r.data
        if (typeof data === 'string' && data.trimStart().toLowerCase().startsWith('<!')) {
          setHealth(
            'Réponse HTML au lieu du JSON /health : la requête ne va pas à FastAPI (ex. base URL = page Vite sans proxy).',
          )
          return
        }
        setHealth(JSON.stringify(data))
      })
      .catch((e) => {
        if (!mounted) return
        setHealth(e?.message || 'Error')
      })
    return () => {
      mounted = false
    }
  }, [baseUrl])

  return (
    <div>
      <PageHeader
        title="Dashboard"
        subtitle="Vérifie la connexion au backend et navigue vers les pages de l’API."
      />

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <Card>
          <div className="text-xs text-zinc-400">API Base URL</div>
          <div className="mt-2 font-mono text-sm text-white">{baseUrl}</div>
        </Card>
        <Card>
          <div className="text-xs text-zinc-400">Health</div>
          <div className="mt-2 font-mono text-sm text-white">{health}</div>
        </Card>
        <Card>
          <div className="text-xs text-zinc-400">Docs</div>
          <a className="mt-2 block text-sm text-violet-300 underline" href={`${baseUrl}/docs`} target="_blank">
            Ouvrir Swagger
          </a>
        </Card>
      </div>
    </div>
  )
}

