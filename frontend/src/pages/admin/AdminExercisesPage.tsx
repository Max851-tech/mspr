import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { api } from '../../lib/api'
import { Button, Card, Input, Label, PageHeader, Table } from '../../components/ui'

type Exercise = {
  exercice_id: number
  nom?: string | null
  muscle_cible?: string | null
  equipement?: string | null
  difficulte?: string | null
}

export function AdminExercisesPage() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [items, setItems] = useState<Exercise[]>([])

  const [nom, setNom] = useState('')
  const [muscle, setMuscle] = useState('')
  const [equipement, setEquipement] = useState('')
  const [difficulte, setDifficulte] = useState('')

  async function load() {
    setLoading(true)
    setError(null)
    try {
      const res = await api.get('/api/v1/exercises', { params: { page: 1, per_page: 25 } })
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
      if (muscle.trim()) payload.muscle_cible = muscle.trim()
      if (equipement.trim()) payload.equipement = equipement.trim()
      if (difficulte.trim()) payload.difficulte = difficulte.trim()
      await api.post('/api/v1/admin/exercises', payload)
      setNom('')
      setMuscle('')
      setEquipement('')
      setDifficulte('')
      await load()
    } catch (e: any) {
      setError(e?.response?.data?.detail || JSON.stringify(e?.response?.data) || e?.message || 'Erreur')
    }
  }

  return (
    <div>
      <PageHeader
        title="Admin — Exercises"
        subtitle="CRUD minimal. La liste utilise /api/v1/exercises (public) et la création utilise /api/v1/admin/exercises."
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
              <Label>Muscle cible</Label>
              <Input value={muscle} onChange={(e) => setMuscle(e.target.value)} />
            </div>
            <div>
              <Label>Équipement</Label>
              <Input value={equipement} onChange={(e) => setEquipement(e.target.value)} />
            </div>
            <div>
              <Label>Difficulté</Label>
              <Input value={difficulte} onChange={(e) => setDifficulte(e.target.value)} placeholder="DEBUTANT|INTERMEDIAIRE|AVANCE" />
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
      </div>
    </div>
  )
}

