import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { api } from '../../lib/api'
import { Button, Card, Input, Label, PageHeader, Table } from '../../components/ui'

type Food = {
  aliment_id: number
  nom: string
  categorie?: string | null
  calories_kcal?: number | null
  deleted_at?: string | null
}

export function AdminFoodsPage() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [items, setItems] = useState<Food[]>([])

  const [nom, setNom] = useState('')
  const [categorie, setCategorie] = useState('')
  const [calories, setCalories] = useState('')

  async function load() {
    setLoading(true)
    setError(null)
    try {
      // public listing endpoint exists; admin has CRUD per id.
      const res = await api.get('/api/v1/foods', { params: { page: 1, per_page: 25 } })
      setItems(res.data?.items ?? [])
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || 'Erreur')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [])

  async function create(e: FormEvent) {
    e.preventDefault()
    setError(null)
    try {
      const payload: any = { nom: nom.trim() }
      if (categorie.trim()) payload.categorie = categorie.trim()
      if (calories.trim()) payload.calories_kcal = Number(calories.trim())

      await api.post('/api/v1/admin/foods', payload)
      setNom('')
      setCategorie('')
      setCalories('')
      await load()
    } catch (e: any) {
      setError(e?.response?.data?.detail || JSON.stringify(e?.response?.data) || e?.message || 'Erreur')
    }
  }

  return (
    <div>
      <PageHeader
        title="Admin — Foods"
        subtitle="CRUD minimal. La liste utilise /api/v1/foods (public) et la création utilise /api/v1/admin/foods."
        right={
          <Button variant="ghost" onClick={load} disabled={loading}>
            Refresh
          </Button>
        }
      />

      {error ? <div className="mb-3 text-sm text-red-300">{error}</div> : null}

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[420px_1fr]">
        <Card>
          <form className="space-y-3" onSubmit={create}>
            <div>
              <Label>Nom</Label>
              <Input value={nom} onChange={(e) => setNom(e.target.value)} required />
            </div>
            <div>
              <Label>Catégorie</Label>
              <Input value={categorie} onChange={(e) => setCategorie(e.target.value)} />
            </div>
            <div>
              <Label>Calories (kcal)</Label>
              <Input value={calories} onChange={(e) => setCalories(e.target.value)} inputMode="decimal" />
            </div>
            <Button type="submit">Create</Button>
            <p className="text-xs text-zinc-500">
              Si tu as 401, configure <span className="font-mono">ADMIN_API_KEY</span> dans Settings.
            </p>
          </form>
        </Card>

        <div>
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
      </div>
    </div>
  )
}

