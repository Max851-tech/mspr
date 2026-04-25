import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { getAccessToken } from '../lib/storage'

/** Routes réservées aux utilisateurs connectés (JWT présent). */
export function RequireAuth() {
  const location = useLocation()
  if (!getAccessToken()) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />
  }
  return <Outlet />
}

/** Connexion / inscription : redirige vers la session si déjà connecté. */
export function GuestOnly() {
  if (getAccessToken()) {
    return <Navigate to="/bienvenue" replace />
  }
  return <Outlet />
}
