import { Outlet } from 'react-router-dom'

/** Mise en page centrée pour login / inscription (sans menu applicatif). */
export function AuthLayout() {
  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100">
      <div className="mx-auto flex min-h-screen w-full max-w-lg flex-col justify-center px-4 py-10">
        <div className="mb-6 text-center">
          <div className="text-lg font-semibold text-white">HealthAI Coach</div>
          <div className="text-xs text-zinc-500">Authentification</div>
        </div>
        <Outlet />
      </div>
    </div>
  )
}
