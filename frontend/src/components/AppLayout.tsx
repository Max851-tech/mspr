import { useEffect, useMemo, useState } from 'react'
import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { clearAccessToken, getAccessToken } from '../lib/storage'

function NavItem({ to, label }: { to: string; label: string }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        [
          'block rounded-lg px-3 py-2 text-sm transition',
          isActive ? 'bg-zinc-800 text-white' : 'text-zinc-300 hover:bg-zinc-900 hover:text-white',
        ].join(' ')
      }
    >
      {label}
    </NavLink>
  )
}

export function AppLayout() {
  const navigate = useNavigate()
  const location = useLocation()
  const [hasToken, setHasToken] = useState(() => Boolean(getAccessToken()))
  const tokenPreview = useMemo(() => {
    const t = getAccessToken()
    if (!t) return ''
    return t.length > 14 ? `${t.slice(0, 10)}…${t.slice(-4)}` : t
  }, [hasToken])

  useEffect(() => {
    setHasToken(Boolean(getAccessToken()))
  }, [location.pathname])

  return (
    <div className="min-h-full">
      <div className="mx-auto grid max-w-7xl grid-cols-1 gap-6 p-4 md:grid-cols-[260px_1fr] md:p-6">
        <aside className="rounded-2xl border border-zinc-800 bg-zinc-950/50 p-4">
          <div className="mb-4">
            <div className="text-sm font-semibold text-white">HealthAI Coach</div>
            <div className="text-xs text-zinc-400">Frontend admin (MSPR)</div>
            {hasToken ? (
              <div className="mt-2 text-[11px] text-zinc-500">
                JWT: <span className="font-mono text-zinc-300">{tokenPreview}</span>
              </div>
            ) : null}
          </div>

          <div className="space-y-1">
            <div className="px-2 pb-2 pt-3 text-[11px] font-semibold uppercase tracking-wider text-zinc-500">
              Général
            </div>
            <NavItem to="/bienvenue" label="Session" />
            <NavItem to="/dashboard" label="Dashboard" />
            <NavItem to="/settings" label="Settings" />

            <div className="px-2 pb-2 pt-4 text-[11px] font-semibold uppercase tracking-wider text-zinc-500">
              Public API
            </div>
            <NavItem to="/foods" label="Foods" />
            <NavItem to="/exercises" label="Exercises" />

            <div className="px-2 pb-2 pt-4 text-[11px] font-semibold uppercase tracking-wider text-zinc-500">
              Admin API
            </div>
            <NavItem to="/admin/users" label="Users" />
            <NavItem to="/admin/foods" label="Foods (CRUD)" />
            <NavItem to="/admin/exercises" label="Exercises (CRUD)" />
          </div>

          {hasToken ? (
            <div className="mt-4 border-t border-zinc-900 pt-4">
              <button
                type="button"
                className="w-full rounded-lg border border-zinc-800 bg-zinc-950 px-3 py-2 text-left text-sm text-zinc-200 hover:bg-zinc-900"
                onClick={() => {
                  clearAccessToken()
                  setHasToken(false)
                  navigate('/login', { replace: true })
                }}
              >
                Déconnexion
              </button>
            </div>
          ) : null}
        </aside>

        <main className="rounded-2xl border border-zinc-800 bg-zinc-950/50 p-4 md:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

