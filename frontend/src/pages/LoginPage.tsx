import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Button, Card, Input, Label, PageHeader } from '../components/ui'
import axios from 'axios'
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
      <PageHeader title="Connexion" subtitle="JWT via /api/v1/auth/token (OAuth2 password)." />

      <Card className="max-w-xl">
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
              navigate('/dashboard', { replace: true })
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
            <Input value={email} onChange={(e) => setEmail(e.target.value)} autoComplete="email" />
          </div>
          <div className="space-y-2">
            <Label>Mot de passe</Label>
            <Input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
            />
          </div>

          {error ? <div className="text-sm text-red-300">{error}</div> : null}

          <div className="flex flex-wrap items-center gap-3">
            <Button type="submit" disabled={loading}>
              {loading ? 'Connexion…' : 'Se connecter'}
            </Button>
            <Link to="/register" className="text-sm text-violet-400 hover:text-violet-300">
              Créer un compte
            </Link>
          </div>
        </form>
      </Card>
    </div>
  )
}
