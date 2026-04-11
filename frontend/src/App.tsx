import { Navigate, Route, Routes } from 'react-router-dom'
import { AppLayout } from './components/AppLayout'
import { DashboardPage } from './pages/DashboardPage'
import { SettingsPage } from './pages/SettingsPage'
import { FoodsPage } from './pages/FoodsPage'
import { ExercisesPage } from './pages/ExercisesPage'
import { AdminUsersPage } from './pages/admin/AdminUsersPage'
import { AdminFoodsPage } from './pages/admin/AdminFoodsPage'
import { AdminExercisesPage } from './pages/admin/AdminExercisesPage'
import { LoginPage } from './pages/LoginPage'
import { RegisterPage } from './pages/RegisterPage'

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/settings" element={<SettingsPage />} />

        <Route path="/foods" element={<FoodsPage />} />
        <Route path="/exercises" element={<ExercisesPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        <Route path="/admin/users" element={<AdminUsersPage />} />
        <Route path="/admin/foods" element={<AdminFoodsPage />} />
        <Route path="/admin/exercises" element={<AdminExercisesPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}

