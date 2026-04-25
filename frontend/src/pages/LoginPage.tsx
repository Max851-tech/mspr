import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import { AuthModeToggle } from '../components/AuthModeToggle'
import { Button, Card, Input, Label } from '../components/ui'
import { api } from '../lib/api'
import { formatApiError } from '../lib/formatApiError'
import { setAccessToken } from '../lib/storage'

type TokenResponse = {
  access_token: string
  token_type: string
}

export function LoginPage() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  return (
    <div>
      <AuthModeToggle active="login" />

      <Card className="border-zinc-800 bg-zinc-900/30">
        <h1 className="mb-1 text-xl font-semibold text-white">Connexion</h1>
        <p className="mb-4 text-sm text-zinc-500">Email et mot de passe enregistrés (le mot de passe est vérifié côté serveur avec le hash stocké).</p>

        <form
          className="space-y-3"
          onSubmit={async (e) => {
            e.preventDefault()
            setError(null)
            setLoading(true)
            try {
              const body = new URLSearchParams()
              body.set('username', email.trim())
              body.set('password', password)
              body.set('grant_type', 'password')

              const { data } = await api.post<TokenResponse>(
                '/api/v1/auth/token',
                body.toString(),
                { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } },
              )

              setAccessToken(data.access_token)
              navigate('/bienvenue', { replace: true, state: { flow: 'login' } })
            } catch (err: unknown) {
              if (axios.isAxiosError(err) && err.response?.status === 401) {
                setError('Email ou mot de passe incorrect.')
              } else {
                setError(
                  formatApiError(
                    err,
                    'Échec de la connexion (vérifie email / mot de passe, et API Base URL dans Settings).',
                  ),
                )
              }
            } finally {
              setLoading(false)
            }
          }}
        >
          <div className="space-y-2">
            <Label>Email</Label>
            <Input
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              type="email"
              autoComplete="email"
              required
            />
          </div>
          <div className="space-y-2">
            <Label>Mot de passe</Label>
            <Input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
              required
            />
          </div>

          {error ? <div className="text-sm text-red-300">{error}</div> : null}

          <Button type="submit" className="mt-2 w-full" disabled={loading}>
            {loading ? 'Connexion…' : 'Se connecter'}
          </Button>
        </form>
      </Card>
    </div>
  )
}
