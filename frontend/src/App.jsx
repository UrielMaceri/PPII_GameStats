import { BrowserRouter, Link, Navigate, Route, Routes } from 'react-router-dom'

import './App.css'
import ABM from './pages/ABM'
import Estadisticas from './pages/Estadisticas'

function Menu() {
  return (
    <div className="app-menu">
      <header className="topbar">
        <Link className="brand" to="/" aria-label="GameStats inicio">
          <span className="brand-mark">G</span>
          <span>GameStats</span>
        </Link>
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
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Menu />} />
        <Route path="/estadisticas" element={<Estadisticas />} />
        <Route
          path="/estadistica"
          element={<Navigate to="/estadisticas" replace />}
        />
        <Route path="/abm" element={<ABM />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
