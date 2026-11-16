const SESSION_KEY = 'gamestats-session'

export function readSession() {
  const savedSession = localStorage.getItem(SESSION_KEY)
  if (!savedSession) {
    return null
  }

  let session
  try {
    session = JSON.parse(savedSession)
  } catch {
    localStorage.removeItem(SESSION_KEY)
    return null
  }
  if (
    !session ||
    !session.accessToken ||
    session.expiresAt <= Date.now() / 1000
  ) {
    localStorage.removeItem(SESSION_KEY)
    return null
  }
  return session
}

export function saveSession(session) {
  localStorage.setItem(SESSION_KEY, JSON.stringify(session))
}

export function clearSession() {
  localStorage.removeItem(SESSION_KEY)
}

export function getAuthHeaders(headers = {}) {
  const session = readSession()
  return session?.accessToken
    ? { ...headers, Authorization: `Bearer ${session.accessToken}` }
    : headers
}
