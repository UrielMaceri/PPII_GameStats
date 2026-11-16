import { useEffect, useState } from 'react'

import { AuthContext } from './context'
import { clearSession, readSession, saveSession } from './session'

export function AuthProvider({ children }) {
  const [session, setSession] = useState(readSession)

  useEffect(() => {
    if (!session) {
      return undefined
    }

    const timeout = window.setTimeout(() => {
      clearSession()
      setSession(null)
    }, Math.max(0, session.expiresAt * 1000 - Date.now()))

    return () => window.clearTimeout(timeout)
  }, [session])

  async function login(username, password) {
    let response
    try {
      response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      })
    } catch (error) {
      throw new Error('No se pudo conectar con el servidor.', { cause: error })
    }

    const result = await response.json()
    if (!response.ok) {
      throw new Error(
        result?.error?.message ?? result?.detail ?? 'No se pudo iniciar sesión.',
      )
    }

    const nextSession = {
      accessToken: result.accessToken,
      expiresAt: result.expiresAt,
      user: result.user,
    }
    saveSession(nextSession)
    setSession(nextSession)
  }

  function logout() {
    clearSession()
    setSession(null)
  }

  return (
    <AuthContext.Provider
      value={{ user: session?.user ?? null, login, logout }}
    >
      {children}
    </AuthContext.Provider>
  )
}
