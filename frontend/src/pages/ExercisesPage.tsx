import { useEffect, useState } from 'react'
import { api } from '../lib/api'
import { Button, Input, PageHeader, Table } from '../components/ui'

type Exercise = {
  exercice_id: number
  nom?: string | null
  muscle_cible?: string | null
  equipement?: string | null
  difficulte?: string | null
}

export function ExercisesPage() {
  const [q, setQ] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [items, setItems] = useState<Exercise[]>([])

  useEffect(() => {
    void search()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  async function search() {
    setLoading(true)
    setError(null)
    try {
      const res = await api.get('/api/v1/exercises', { params: { q: q.trim() || undefined, page: 1, per_page: 25 } })
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
        title="Exercises (public)"
        subtitle="Recherche dans le catalogue exercices via /api/v1/exercises"
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
            <th className="px-3 py-2">Muscle</th>
            <th className="px-3 py-2">Équipement</th>
            <th className="px-3 py-2">Difficulté</th>
          </tr>
        </thead>
        <tbody>
          {items.map((ex) => (
            <tr key={ex.exercice_id} className="border-t border-zinc-900">
              <td className="px-3 py-2 font-mono text-xs text-zinc-400">{ex.exercice_id}</td>
              <td className="px-3 py-2">{ex.nom || ''}</td>
              <td className="px-3 py-2 text-zinc-300">{ex.muscle_cible || ''}</td>
              <td className="px-3 py-2 text-zinc-300">{ex.equipement || ''}</td>
              <td className="px-3 py-2 text-zinc-300">{ex.difficulte || ''}</td>
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

