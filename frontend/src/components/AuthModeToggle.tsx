import { Link } from 'react-router-dom'

const base =
  'flex-1 rounded-lg px-3 py-2 text-center text-sm font-medium transition border border-zinc-800'

export function AuthModeToggle({ active }: { active: 'login' | 'register' }) {
  return (
    <div className="mb-4 flex gap-2 rounded-xl border border-zinc-800 bg-zinc-900/40 p-1">
      <Link
        to="/login"
        className={
          active === 'login'
            ? `${base} bg-violet-600 text-white border-violet-500`
            : `${base} text-zinc-400 hover:border-zinc-600 hover:text-white`
        }
      >
        Connexion
      </Link>
      <Link
        to="/register"
        className={
          active === 'register'
            ? `${base} bg-violet-600 text-white border-violet-500`
            : `${base} text-zinc-400 hover:border-zinc-600 hover:text-white`
        }
      >
        Inscription
      </Link>
    </div>
  )
}
