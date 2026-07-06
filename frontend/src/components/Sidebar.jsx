import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../AuthContext'

const links = [
  { to: '/', label: 'Overview', end: true },
  { to: '/loans', label: 'Loans' },
  { to: '/financial-profile', label: 'Financial profile' },
  { to: '/settlements', label: 'Settlements' },
  { to: '/negotiations', label: 'AI negotiations' },
]

export default function Sidebar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <span className="sidebar-mark">FR</span>
        <div>
          <div className="sidebar-title">FinRelief AI</div>
          <div className="sidebar-subtitle">Recovery workspace</div>
        </div>
      </div>

      <nav className="sidebar-nav">
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.end}
            className={({ isActive }) => 'sidebar-link' + (isActive ? ' is-active' : '')}
          >
            {link.label}
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-user">
          <div className="sidebar-user-name">{user?.name}</div>
          <div className="sidebar-user-email">{user?.email}</div>
        </div>
        <button className="btn btn-ghost" onClick={handleLogout}>Sign out</button>
      </div>
    </aside>
  )
}
