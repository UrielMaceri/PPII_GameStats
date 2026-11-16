import { useState } from 'react'
import { Link } from 'react-router-dom'

import ConsolasTab from '../components/estadisticas/ConsolasTab'
import VideojuegosTab from '../components/estadisticas/VideojuegosTab'

const tabs = [
  { id: 'consolas', label: 'Consolas' },
  { id: 'videojuegos', label: 'Videojuegos' },
]

export default function Estadisticas() {
  const [activeTab, setActiveTab] = useState('consolas')

  return (
    <>
      <header className="topbar">
        <Link className="brand" to="/">
          <span className="brand-mark">G</span>
          <span>GameStats</span>
        </Link>
        <Link className="secondary-button app-link-button" to="/">
          Volver al menú
        </Link>
      </header>

      <main className="dashboard">
        <section className="page-heading">
          <div>
            <p className="eyebrow">PANEL DE ESTADÍSTICAS</p>
            <h1>Estadísticas</h1>
            <p className="page-description">
              Explora los datos de consolas y videojuegos.
            </p>
          </div>
          <span className="updated-label">Ventas expresadas en millones</span>
        </section>

        <div className="statistics-tabs" role="tablist" aria-label="Tipo de estadísticas">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              id={`tab-${tab.id}`}
              className={`statistics-tab${activeTab === tab.id ? ' active' : ''}`}
              type="button"
              role="tab"
              aria-selected={activeTab === tab.id}
              aria-controls={`panel-${tab.id}`}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <div
          id={`panel-${activeTab}`}
          role="tabpanel"
          aria-labelledby={`tab-${activeTab}`}
          tabIndex={0}
        >
          {activeTab === 'consolas' ? <ConsolasTab /> : <VideojuegosTab />}
        </div>
      </main>

      <footer className="footer">
        GameStats <span>•</span> Panel de consolas y videojuegos
      </footer>
    </>
  )
}
