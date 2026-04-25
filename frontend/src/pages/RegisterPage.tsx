import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { AuthModeToggle } from '../components/AuthModeToggle'
import { Button, Card, Input, Label } from '../components/ui'
import { api } from '../lib/api'
import { formatApiError } from '../lib/formatApiError'
import { setAccessToken } from '../lib/storage'

type RegisterResponse = {
  user: {
    utilisateur_id: number
    email: string | null
    nom_utilisateur: string
    role: string
    statut: string
    cree_le: string
  }
  access_token: string
  token_type: string
}

export function RegisterPage() {
  const navigate = useNavigate()
  const [nom, setNom] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [password2, setPassword2] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  return (
    <div>
      <AuthModeToggle active="register" />

      <Card className="border-zinc-800 bg-zinc-900/30">
        <h1 className="mb-1 text-xl font-semibold text-white">Créer un compte</h1>
        <p className="mb-4 text-sm text-zinc-500">
          Champs obligatoires : <strong className="text-zinc-400">nom affiché</strong>,{' '}
          <strong className="text-zinc-400">email</strong>, <strong className="text-zinc-400">mot de passe</strong> (au
          moins 8 caractères) et confirmation. Le mot de passe est{' '}
          <strong className="text-zinc-400">haché</strong> avant d’être enregistré ; le rôle par défaut est{' '}
          <strong className="text-zinc-400">utilisateur</strong>.
        </p>

        <form
          className="space-y-3"
          onSubmit={async (e) => {
            e.preventDefault()
            setError(null)
            if (password !== password2) {
              setError('Les deux mots de passe ne correspondent pas.')
              return
            }
            if (password.length < 8) {
              setError('Le mot de passe doit faire au moins 8 caractères.')
              return
            }
            if (!nom.trim()) {
              setError('Le nom affiché est obligatoire.')
              return
            }
            setLoading(true)
            try {
              const { data } = await api.post<RegisterResponse>('/api/v1/auth/register', {
                email: email.trim(),
                mot_de_passe: password,
                nom: nom.trim(),
              })
              setAccessToken(data.access_token)
              navigate('/bienvenue', { replace: true, state: { flow: 'register' } })
            } catch (err: unknown) {
              const ax = err as { response?: { status?: number; data?: { detail?: unknown } } }
              if (ax.response?.status === 409) {
                setError('Cet email est déjà utilisé.')
              } else if (ax.response?.status === 422) {
                setError('Données invalides (email, nom ou mot de passe).')
              } else {
                setError(formatApiError(err, "Inscription impossible (vérifie l'API Base URL dans Settings)."))
              }
            } finally {
              setLoading(false)
            }
          }}
        >
          <div className="space-y-2">
            <Label>Nom affiché *</Label>
            <Input value={nom} onChange={(e) => setNom(e.target.value)} autoComplete="name" required minLength={1} />
          </div>
          <div className="space-y-2">
            <Label>Email *</Label>
            <Input value={email} onChange={(e) => setEmail(e.target.value)} type="email" autoComplete="email" required />
          </div>
          <div className="space-y-2">
            <Label>Mot de passe * (min. 8 caractères)</Label>
            <Input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="new-password"
              required
              minLength={8}
            />
          </div>
          <div className="space-y-2">
            <Label>Confirmer le mot de passe *</Label>
            <Input
              type="password"
              value={password2}
              onChange={(e) => setPassword2(e.target.value)}
              autoComplete="new-password"
              required
              minLength={8}
            />
          </div>

          {error ? <div className="text-sm text-red-300">{error}</div> : null}

          <Button type="submit" className="mt-2 w-full" disabled={loading}>
            {loading ? 'Création…' : "S'inscrire"}
          </Button>
        </form>
      </Card>
    </div>
  )
}
