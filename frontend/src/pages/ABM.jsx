import { Link } from 'react-router-dom'

import VideojuegosTab from '../components/abm/VideojuegosTab'

const tabs = [
  { id: 'videojuegos', label: 'Videojuegos', active: true },
  { id: 'consolas', label: 'Consolas', stage: 2 },
  { id: 'desarrolladores', label: 'Desarrolladores', stage: 3 },
  { id: 'publishers', label: 'Publishers', stage: 4 },
]

export default function ABM() {
  return (
    <div className="app-menu">
      <header className="topbar">
        <Link className="brand" to="/">
          <span className="brand-mark">G</span>
          <span>GameStats</span>
        </Link>
        <Link className="secondary-button app-link-button" to="/">
          Volver al menú
        </Link>
      </header>

      <main className="dashboard app-menu-content">
        <section className="page-heading">
          <div>
            <p className="eyebrow">GESTIÓN DEL CATÁLOGO</p>
            <h1>ABM</h1>
            <p className="page-description">
              Administra los videojuegos y sus relaciones con el catálogo.
            </p>
          </div>
        </section>

        <div className="statistics-tabs abm-tabs" role="tablist" aria-label="Tipo de catálogo">
          {tabs.filter((tab) => tab.active).map((tab) => (
            <button
              key={tab.id}
              className={`statistics-tab${tab.active ? ' active' : ''}`}
              type="button"
              role="tab"
              aria-selected={Boolean(tab.active)}
              aria-label={
                tab.stage
                  ? `${tab.label}, etapa ${tab.stage}, próximamente`
                  : tab.label
              }
            >
              {tab.label}
              {tab.stage && (
                <span className="tab-stage">Etapa {tab.stage}</span>
              )}
            </button>
          ))}
        </div>

        <VideojuegosTab />
      </main>

      <footer className="footer">
        GameStats <span>•</span> Administración del catálogo
      </footer>
    </div>
  )
}
