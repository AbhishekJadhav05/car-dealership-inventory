import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react'
import { api, ApiError } from '@/lib/api'
import type { AuthToken, User } from '@/types'

interface AuthState {
  token: string | null
  user: User | null
  loading: boolean
}

interface AuthActions {
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<(AuthState & AuthActions) | null>(null)

const TOKEN_KEY = 'auth_token'

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(() =>
    localStorage.getItem(TOKEN_KEY),
  )
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  // Fetch /me whenever token changes
  useEffect(() => {
    if (!token) {
      setUser(null)
      setLoading(false)
      return
    }
    setLoading(true)
    api
      .get<User>('/api/auth/me', token)
      .then(setUser)
      .catch(() => {
        // Token invalid / expired — clear it
        localStorage.removeItem(TOKEN_KEY)
        setToken(null)
        setUser(null)
      })
      .finally(() => setLoading(false))
  }, [token])

  const login = useCallback(async (email: string, password: string) => {
    const data = await api.post<AuthToken>('/api/auth/login', { email, password })
    localStorage.setItem(TOKEN_KEY, data.access_token)
    setToken(data.access_token)
  }, [])

  const register = useCallback(async (email: string, password: string) => {
    await api.post<User>('/api/auth/register', { email, password })
    // Auto-login after registration
    const data = await api.post<AuthToken>('/api/auth/login', { email, password })
    localStorage.setItem(TOKEN_KEY, data.access_token)
    setToken(data.access_token)
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY)
    setToken(null)
    setUser(null)
  }, [])

  const value = useMemo(
    () => ({ token, user, loading, login, register, logout }),
    [token, user, loading, login, register, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}

export function useRequireAuth() {
  const auth = useAuth()
  if (auth.loading) return auth
  if (!auth.token || !auth.user) throw new Error('Not authenticated')
  return auth as AuthState & AuthActions & { token: string; user: User }
}

export { ApiError }
