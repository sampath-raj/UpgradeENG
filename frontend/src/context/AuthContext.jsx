import { createContext, useContext, useState, useEffect } from 'react'
import { authAPI, saveToken, clearToken } from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      authAPI.me()
        .then((res) => setUser(res.data))
        .catch(() => clearToken())
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  const login = async (email, password) => {
    const res = await authAPI.login({ email, password })
    saveToken(res.data.access_token)
    const userRes = await authAPI.me()
    setUser(userRes.data)
    return userRes.data
  }

  const signup = async (name, email, password) => {
    const res = await authAPI.signup({ name, email, password })
    saveToken(res.data.access_token)
    const userRes = await authAPI.me()
    setUser(userRes.data)
    return userRes.data
  }

  const logout = () => {
    clearToken()
    setUser(null)
  }

  const refreshUser = async () => {
    try {
      const res = await authAPI.me()
      setUser(res.data)
    } catch (e) {
      // ignore
    }
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, signup, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
