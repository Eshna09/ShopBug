import { useState } from 'react'
import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const navItems = [
  { to: '/', label: 'Home' },
  { to: '/products', label: 'Products' },
  { to: '/cart', label: 'Cart' },
  { to: '/orders', label: 'Orders' },
]

export default function Header() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [mobileOpen, setMobileOpen] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  const linkClass = ({ isActive }) =>
    `rounded-md px-3 py-2 text-sm font-medium transition-colors ${
      isActive
        ? 'bg-brand-50 text-brand-700'
        : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
    }`

  return (
    <header className="sticky top-0 z-50 border-b border-gray-200 bg-white/95 backdrop-blur">
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2">
          <span className="text-2xl">🐛</span>
          <span className="text-xl font-bold tracking-tight text-gray-900">
            Shop<span className="text-brand-600">Bug</span>
          </span>
        </Link>

        {/* Desktop nav */}
        <div className="hidden items-center gap-1 md:flex">
          {navItems.map((item) => (
            <NavLink key={item.to} to={item.to} className={linkClass} end={item.to === '/'}>
              {item.label}
            </NavLink>
          ))}

          {user ? (
            <div className="ml-2 flex items-center gap-3 border-l border-gray-200 pl-4">
              <span className="text-sm text-gray-500">{user.email}</span>
              <button onClick={handleLogout} className="btn-secondary text-xs">
                Logout
              </button>
            </div>
          ) : (
            <div className="ml-2 flex items-center gap-2 border-l border-gray-200 pl-4">
              <Link to="/login" className="btn-secondary text-xs">
                Login
              </Link>
              <Link to="/register" className="btn-primary text-xs">
                Register
              </Link>
            </div>
          )}
        </div>

        {/* Mobile toggle */}
        <button
          className="rounded-md p-2 text-gray-600 hover:bg-gray-100 md:hidden"
          onClick={() => setMobileOpen((v) => !v)}
          aria-label="Toggle navigation"
        >
          <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            {mobileOpen ? (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            ) : (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            )}
          </svg>
        </button>
      </nav>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="border-t border-gray-200 bg-white px-4 py-3 md:hidden">
          <div className="flex flex-col gap-1">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={linkClass}
                end={item.to === '/'}
                onClick={() => setMobileOpen(false)}
              >
                {item.label}
              </NavLink>
            ))}
            {user ? (
              <div className="mt-2 flex items-center justify-between border-t border-gray-100 pt-2">
                <span className="text-sm text-gray-500">{user.email}</span>
                <button onClick={handleLogout} className="btn-secondary text-xs">
                  Logout
                </button>
              </div>
            ) : (
              <div className="mt-2 flex gap-2 border-t border-gray-100 pt-2">
                <Link to="/login" className="btn-secondary flex-1 text-xs" onClick={() => setMobileOpen(false)}>
                  Login
                </Link>
                <Link to="/register" className="btn-primary flex-1 text-xs" onClick={() => setMobileOpen(false)}>
                  Register
                </Link>
              </div>
            )}
          </div>
        </div>
      )}
    </header>
  )
}
