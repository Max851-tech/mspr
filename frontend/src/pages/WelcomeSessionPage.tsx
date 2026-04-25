import { useEffect, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { Button, Card } from '../components/ui'
import { api } from '../lib/api'
import { clearAccessToken } from '../lib/storage'

type SessionState = {
  flow?: 'login' | 'register'
}

type UserMe = {
  utilisateur_id: number
  email: string | null
  nom_utilisateur: string
  role: string
  statut: string
  cree_le: string
}

function roleLabel(role: string): string {
  if (role === 'ADMIN') return 'administrateur'
  return 'utilisateur normal'
}

function formatDbDate(iso: string): string {
  try {
    return new Date(iso).toLocaleString('fr-FR')
  } catch {
    return iso
  }
}

export function WelcomeSessionPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const [user, setUser] = useState<UserMe | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  const state = (location.state || {}) as SessionState
  const flow = state.flow

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)
    api
      .get<UserMe>('/api/v1/auth/me')
      .then((r) => {
        if (!cancelled) {
          setUser(r.data)
        }
      })
      .catch(() => {
        if (!cancelled) setError('Session invalide. Reconnecte-toi.')
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [location.key])

  const signOut = () => {
    clearAccessToken()
    navigate('/login', { replace: true })
  }

  const mainText = () => {
    if (error) return error
    if (loading || !user) return 'Chargement des données depuis la base…'
    const role = roleLabel(user.role)
    if (flow === 'register') {
      return `Vous avez créé un compte (rôle : ${role}).`
    }
    return `Vous êtes connecté avec le compte ${user.nom_utilisateur} (rôle : ${role}).`
  }

  return (
    <div className="min-h-screen bg-zinc-950">
      <div className="mx-auto flex min-h-screen max-w-lg flex-col px-4 py-12">
        <div className="flex flex-1 flex-col items-center justify-center gap-6 text-center">
          <p className="text-lg text-white md:text-xl">{mainText()}</p>

          {user && !error ? (
            <Card className="w-full border-zinc-800 bg-zinc-900/40 text-left">
              <div className="mb-2 text-xs font-semibold uppercase tracking-wider text-zinc-500">
                Enregistré en base (table utilisateur)
              </div>
              <dl className="grid grid-cols-1 gap-2 text-sm text-zinc-300 sm:grid-cols-2">
                <div>
                  <dt className="text-zinc-500">ID</dt>
                  <dd className="font-mono text-white">{user.utilisateur_id}</dd>
                </div>
                <div>
                  <dt className="text-zinc-500">Email</dt>
                  <dd className="text-white">{user.email ?? '—'}</dd>
                </div>
                <div>
                  <dt className="text-zinc-500">Nom affiché</dt>
                  <dd className="text-white">{user.nom_utilisateur}</dd>
                </div>
                <div>
                  <dt className="text-zinc-500">Rôle</dt>
                  <dd className="text-white">{user.role}</dd>
                </div>
                <div>
                  <dt className="text-zinc-500">Statut</dt>
                  <dd className="text-white">{user.statut}</dd>
                </div>
                <div>
                  <dt className="text-zinc-500">Créé le</dt>
                  <dd className="font-mono text-xs text-white">{formatDbDate(user.cree_le)}</dd>
                </div>
              </dl>
              <p className="mt-3 border-t border-zinc-800 pt-3 text-xs text-zinc-500">
                Le mot de passe est stocké uniquement en <strong className="text-zinc-400">hash</strong> dans la colonne{' '}
                <span className="font-mono">mot_de_passe_hash</span> ; il n’est jamais renvoyé par l’API.
              </p>
            </Card>
          ) : null}

          {user?.role === 'ADMIN' ? (
            <p className="max-w-md text-sm text-zinc-500">
              La création ou la promotion d’autres comptes administrateurs est gérée par l’équipe (procédure interne ou
              base de données), pas depuis cette page d’inscription publique.
            </p>
          ) : null}
        </div>

        <div className="mt-auto flex flex-col items-center gap-4 border-t border-zinc-800 pt-8">
          <Button variant="ghost" type="button" onClick={signOut}>
            Sign out
          </Button>
        </div>
      </div>
    </div>
  )
}
