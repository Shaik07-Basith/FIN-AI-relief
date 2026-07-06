import { Navigate, Route, Routes } from 'react-router-dom'
import { useAuth } from './AuthContext'
import Sidebar from './components/Sidebar'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Loans from './pages/Loans'
import FinancialProfile from './pages/FinancialProfile'
import Settlements from './pages/Settlements'
import Negotiations from './pages/Negotiations'

function ProtectedLayout({ children }) {
  const { user, loading } = useAuth()

  if (loading) return <div className="page-loading">Loading FinRelief AI…</div>
  if (!user) return <Navigate to="/login" replace />

  return (
    <div className="app-shell">
      <Sidebar />
      <main className="app-main">{children}</main>
    </div>
  )
}

export default function App() {
  const { user, loading } = useAuth()

  return (
    <Routes>
      <Route
        path="/login"
        element={!loading && user ? <Navigate to="/" replace /> : <Login />}
      />
      <Route
        path="/register"
        element={!loading && user ? <Navigate to="/" replace /> : <Register />}
      />
      <Route path="/" element={<ProtectedLayout><Dashboard /></ProtectedLayout>} />
      <Route path="/loans" element={<ProtectedLayout><Loans /></ProtectedLayout>} />
      <Route path="/financial-profile" element={<ProtectedLayout><FinancialProfile /></ProtectedLayout>} />
      <Route path="/settlements" element={<ProtectedLayout><Settlements /></ProtectedLayout>} />
      <Route path="/negotiations" element={<ProtectedLayout><Negotiations /></ProtectedLayout>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
