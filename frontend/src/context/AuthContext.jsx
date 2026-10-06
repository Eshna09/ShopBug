import { createContext, useContext, useState, useCallback, useEffect } from 'react'
import { authApi } from '../services/api'

const AuthContext = createContext(null)

const STORAGE_KEY = 'shopbug_user'

/** Read the persisted user from localStorage on initial load. */
function loadUser() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(loadUser)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // Keep localStorage in sync whenever the user changes.
  useEffect(() => {
    if (user) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(user))
    } else {
      localStorage.removeItem(STORAGE_KEY)
    }
  }, [user])

  const register = useCallback(async (email, password) => {
    setLoading(true)
    setError(null)
    try {
      const data = await authApi.register(email, password)
      // The register endpoint returns { id, email } — log the user in
      // immediately so they can start shopping without a separate login step.
      const newUser = { id: data.id, email: data.email }
      setUser(newUser)
      return newUser
    } catch (err) {
      setError(err.message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  const login = useCallback(async (email, password) => {
    setLoading(true)
    setError(null)
    try {
      const data = await authApi.login(email, password)
      const newUser = { id: data.id, email: data.email }
      setUser(newUser)
      return newUser
    } catch (err) {
      setError(err.message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  const logout = useCallback(() => {
    setUser(null)
    setError(null)
  }, [])

  const clearError = useCallback(() => setError(null), [])

  return (
    <AuthContext.Provider
      value={{ user, loading, error, register, login, logout, clearError }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within an AuthProvider')
  return ctx
}
