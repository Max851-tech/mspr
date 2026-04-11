import { Navigate, Route, Routes } from 'react-router-dom'
import { AppLayout } from './components/AppLayout'
import { AuthLayout } from './components/AuthLayout'
import { GuestOnly, RequireAuth } from './components/AuthGuards'
import { DashboardPage } from './pages/DashboardPage'
import { SettingsPage } from './pages/SettingsPage'
import { FoodsPage } from './pages/FoodsPage'
import { ExercisesPage } from './pages/ExercisesPage'
import { AdminUsersPage } from './pages/admin/AdminUsersPage'
import { AdminFoodsPage } from './pages/admin/AdminFoodsPage'
import { AdminExercisesPage } from './pages/admin/AdminExercisesPage'
import { LoginPage } from './pages/LoginPage'
import { RegisterPage } from './pages/RegisterPage'
import { WelcomeSessionPage } from './pages/WelcomeSessionPage'
import { getAccessToken } from './lib/storage'

function RootRedirect() {
  if (getAccessToken()) {
    return <Navigate to="/bienvenue" replace />
  }
  return <Navigate to="/login" replace />
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<RootRedirect />} />

      <Route element={<GuestOnly />}>
        <Route element={<AuthLayout />}>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
        </Route>
      </Route>

      <Route element={<RequireAuth />}>
        <Route path="/bienvenue" element={<WelcomeSessionPage />} />
        <Route element={<AppLayout />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="/foods" element={<FoodsPage />} />
          <Route path="/exercises" element={<ExercisesPage />} />
          <Route path="/admin/users" element={<AdminUsersPage />} />
          <Route path="/admin/foods" element={<AdminFoodsPage />} />
          <Route path="/admin/exercises" element={<AdminExercisesPage />} />
        </Route>
      </Route>

      <Route path="*" element={<RootRedirect />} />
    </Routes>
  )
}
