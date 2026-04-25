import { useEffect, useMemo, useState } from 'react'
import { api } from '../lib/api'
import { Button, Input, PageHeader, Table } from '../components/ui'

type Food = {
  aliment_id: number
  nom: string
  categorie?: string | null
  calories_kcal?: number | null
}

export function FoodsPage() {
  const [q, setQ] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [items, setItems] = useState<Food[]>([])

  const canSearch = useMemo(() => q.trim().length >= 0, [q])

  useEffect(() => {
    // initial load
    void search()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  async function search() {
    if (!canSearch) return
    setLoading(true)
    setError(null)
    try {
      const res = await api.get('/api/v1/foods', { params: { q: q.trim() || undefined, page: 1, per_page: 25 } })
      setItems(res.data?.items ?? [])
    } catch (e: any) {
      setError(e?.message || 'Erreur')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <PageHeader
        title="Foods (public)"
        subtitle="Recherche dans le référentiel aliments via /api/v1/foods"
        right={
          <div className="flex gap-2">
            <Input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Rechercher…" />
            <Button onClick={search} disabled={loading}>
              {loading ? '…' : 'Search'}
            </Button>
          </div>
        }
      />

      {error ? <div className="mb-3 text-sm text-red-300">{error}</div> : null}

      <Table>
        <thead className="bg-zinc-950">
          <tr className="text-xs text-zinc-400">
            <th className="px-3 py-2">ID</th>
            <th className="px-3 py-2">Nom</th>
            <th className="px-3 py-2">Catégorie</th>
            <th className="px-3 py-2">Calories</th>
          </tr>
        </thead>
        <tbody>
          {items.map((f) => (
            <tr key={f.aliment_id} className="border-t border-zinc-900">
              <td className="px-3 py-2 font-mono text-xs text-zinc-400">{f.aliment_id}</td>
              <td className="px-3 py-2">{f.nom}</td>
              <td className="px-3 py-2 text-zinc-300">{f.categorie || ''}</td>
              <td className="px-3 py-2 text-zinc-300">{f.calories_kcal ?? ''}</td>
            </tr>
          ))}
          {!items.length ? (
            <tr>
              <td className="px-3 py-8 text-center text-sm text-zinc-500" colSpan={4}>
                Aucun résultat
              </td>
            </tr>
          ) : null}
        </tbody>
      </Table>
    </div>
  )
}

