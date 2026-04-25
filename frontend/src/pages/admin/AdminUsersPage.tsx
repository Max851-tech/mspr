import { useEffect, useState } from 'react'
import { api } from '../../lib/api'
import { getApiBaseUrl } from '../../lib/storage'
import { Button, PageHeader, Table } from '../../components/ui'

type User = {
  utilisateur_id: number
  email?: string | null
  nom_utilisateur: string
  role: string
  statut: string
  cree_le: string
}

export function AdminUsersPage() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [items, setItems] = useState<User[]>([])
  const baseUrl = getApiBaseUrl()

  async function load() {
    setLoading(true)
    setError(null)
    try {
      const res = await api.get('/api/v1/admin/users', { params: { page: 1, limit: 25 } })
      setItems(res.data?.items ?? [])
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || 'Erreur')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [baseUrl])

  return (
    <div>
      <PageHeader
        title="Admin — Users"
        subtitle="Nécessite X-API-Key. Si tu as 401, configure la clé dans Settings."
        right={
          <div className="flex gap-2">
            <Button variant="ghost" onClick={load} disabled={loading}>
              Refresh
            </Button>
            <a
              className="rounded-lg bg-zinc-900 px-3 py-2 text-sm font-medium text-zinc-200 hover:bg-zinc-800"
              href={`${baseUrl}/api/v1/admin/users/export`}
              target="_blank"
              rel="noreferrer"
            >
              Export CSV
            </a>
          </div>
        }
      />

      {error ? <div className="mb-3 text-sm text-red-300">{error}</div> : null}

      <Table>
        <thead className="bg-zinc-950">
          <tr className="text-xs text-zinc-400">
            <th className="px-3 py-2">ID</th>
            <th className="px-3 py-2">Email</th>
            <th className="px-3 py-2">Nom</th>
            <th className="px-3 py-2">Role</th>
            <th className="px-3 py-2">Statut</th>
          </tr>
        </thead>
        <tbody>
          {items.map((u) => (
            <tr key={u.utilisateur_id} className="border-t border-zinc-900">
              <td className="px-3 py-2 font-mono text-xs text-zinc-400">{u.utilisateur_id}</td>
              <td className="px-3 py-2">{u.email || ''}</td>
              <td className="px-3 py-2">{u.nom_utilisateur}</td>
              <td className="px-3 py-2 text-zinc-300">{u.role}</td>
              <td className="px-3 py-2 text-zinc-300">{u.statut}</td>
            </tr>
          ))}
          {!items.length ? (
            <tr>
              <td className="px-3 py-8 text-center text-sm text-zinc-500" colSpan={5}>
                Aucun résultat
              </td>
            </tr>
          ) : null}
        </tbody>
      </Table>
    </div>
  )
}

