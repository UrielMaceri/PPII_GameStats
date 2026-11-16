import { useState } from 'react'
import {
  BrowserRouter,
  Link,
  Navigate,
  Route,
  Routes,
  useNavigate,
} from 'react-router-dom'

import { AuthProvider } from './auth/AuthContext'
import { useAuth } from './auth/useAuth'
import './App.css'
import ABM from './pages/ABM'
import Estadisticas from './pages/Estadisticas'

function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setIsSubmitting(true)
    try {
      await login(username, password)
      navigate('/', { replace: true })
    } catch (loginError) {
      setError(loginError.message)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="state-screen">
      <section className="login-card">
        <div className="brand login-brand">
          <span className="brand-mark">G</span>
          <span>GameStats</span>
        </div>
        <p className="eyebrow">ACCESO A LA PLATAFORMA</p>
        <h1>Iniciar sesión</h1>
        <p className="login-description">
          Ingresa con tu usuario para acceder a las secciones habilitadas.
        </p>
        <form className="login-form" onSubmit={handleSubmit}>
          <label className="game-form-field" htmlFor="username">
            Usuario
            <input
              id="username"
              name="username"
              autoComplete="username"
              required
              value={username}
              onChange={(event) => setUsername(event.target.value)}
            />
          </label>
          <label className="game-form-field" htmlFor="password">
            Contraseña
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={(event) => setPassword(event.target.value)}
            />
          </label>
          {error && <p className="login-error" role="alert">{error}</p>}
          <button className="primary-button login-submit" disabled={isSubmitting}>
            {isSubmitting ? 'Ingresando…' : 'Ingresar'}
          </button>
        </form>
        <p className="login-hint">
          Acceso inicial: <strong>admin / admin123</strong> o{' '}
          <strong>usuario / usuario123</strong>.
        </p>
      </section>
    </main>
  )
}

function Home() {
  const { user } = useAuth()
  return user ? <Menu /> : <Navigate to="/login" replace />
}

function ProtectedRoute({ children, adminOnly = false }) {
  const { user } = useAuth()
  if (!user) {
    return <Navigate to="/login" replace />
  }
  if (adminOnly && user.role !== 'admin') {
    return <Navigate to="/" replace />
  }
  return children
}

function Menu() {
  const { user, logout } = useAuth()

  return (
    <div className="app-menu">
      <header className="topbar">
        <Link className="brand" to="/" aria-label="GameStats inicio">
          <span className="brand-mark">G</span>
          <span>GameStats</span>
        </Link>
        <div className="session-controls">
          <span className="session-user">{user.username}</span>
          <button className="secondary-button" type="button" onClick={logout}>
            Cerrar sesión
          </button>
        </div>
      </header>

      <main className="dashboard app-menu-content">
        <section className="page-heading">
          <div>
            <p className="eyebrow">OBSERVATORIO DE VIDEOJUEGOS</p>
            <h1>GameStats</h1>
            <p className="page-description">
              Elige una sección para continuar.
            </p>
          </div>
        </section>

        <section className="app-menu-grid" aria-label="Secciones de GameStats">
          <Link className="app-menu-card" to="/estadisticas">
            <span className="eyebrow">EXPLORAR DATOS</span>
            <h2>Estadísticas</h2>
            <p>
              Consulta las métricas de consolas y videojuegos, y filtra los datos
              de videojuegos.
            </p>
            <span className="app-menu-link">
              Abrir estadísticas <span aria-hidden="true">→</span>
            </span>
          </Link>

          {user.role === 'admin' && (
            <Link className="app-menu-card" to="/abm">
              <span className="eyebrow">GESTIONAR CATÁLOGO</span>
              <h2>ABM</h2>
              <p>
                Accede a la pantalla de gestión del catálogo, que se organizará
                más adelante.
              </p>
              <span className="app-menu-link">
                Abrir ABM <span aria-hidden="true">→</span>
              </span>
            </Link>
          )}
        </section>
      </main>

      <footer className="footer">
        GameStats <span>•</span> Consolas y videojuegos
      </footer>
    </div>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route
            path="/login"
            element={<LoginRedirect />}
          />
          <Route
            path="/estadisticas"
            element={
              <ProtectedRoute>
                <Estadisticas />
              </ProtectedRoute>
            }
          />
          <Route
            path="/estadistica"
            element={<Navigate to="/estadisticas" replace />}
          />
          <Route
            path="/abm"
            element={
              <ProtectedRoute adminOnly>
                <ABM />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}

function LoginRedirect() {
  const { user } = useAuth()
  return user ? <Navigate to="/" replace /> : <Login />
}
