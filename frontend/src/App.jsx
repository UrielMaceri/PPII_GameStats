import { useEffect, useState } from 'react'
import './App.css'

const numberFormat = new Intl.NumberFormat('es-AR', {
  maximumFractionDigits: 1,
})

const initialFilters = {
  yearFrom: '',
  yearTo: '',
  generationId: '',
  manufacturerId: '',
  consoleId: '',
  publisherId: '',
}

const gameEndpoints = {
  summary: '/api/estadisticas/resumen',
  salesByGeneration: '/api/estadisticas/ventas-por-generacion',
  salesByConsole: '/api/estadisticas/ventas-por-consola',
  salesByManufacturer: '/api/estadisticas/ventas-por-fabricante',
  publishers: '/api/estadisticas/ranking-publishers?limit=10',
  developers: '/api/estadisticas/ranking-desarrolladores?limit=10',
  years: '/api/estadisticas/ventas-por-anio',
  topGames: '/api/estadisticas/juegos-mas-vendidos?limit=10',
  dominantManufacturers: '/api/estadisticas/dominador-por-generacion',
}

function formatNumber(value) {
  return numberFormat.format(value)
}

async function requestJson(path, signal) {
  const response = await fetch(path, { signal })
  if (!response.ok) {
    throw new Error(`La API respondió con estado ${response.status}.`)
  }

  const result = await response.json()
  if (!result.data || !result.meta) {
    throw new Error('La respuesta de estadísticas tiene un formato inválido.')
  }
  return result.data
}

async function requestItems(path, signal) {
  const response = await fetch(path, { signal })
  if (!response.ok) {
    throw new Error(`La API respondió con estado ${response.status}.`)
  }

  const result = await response.json()
  if (!Array.isArray(result.data)) {
    throw new Error('La respuesta del catálogo tiene un formato inválido.')
  }
  return result.data
}

function withFilters(endpoint, filters) {
  const params = new URLSearchParams()
  Object.entries(filters).forEach(([key, value]) => {
    if (value) {
      params.set(key, value)
    }
  })
  if (!params.size) {
    return endpoint
  }
  return `${endpoint}${endpoint.includes('?') ? '&' : '?'}${params.toString()}`
}

function ChartCard({ eyebrow, title, description, index, wide = false, children }) {
  return (
    <article className={`chart-card${wide ? ' chart-card-wide' : ''}`}>
      <div className="chart-heading">
        <div>
          <p className="eyebrow">{eyebrow}</p>
          <h3>{title}</h3>
          <p>{description}</p>
        </div>
        <span className="chart-index">{index}</span>
      </div>
      {children}
    </article>
  )
}

function BarChart({ items, valueKey = 'sales', unit = ' M', color = 'blue' }) {
  if (!items.length) {
    return <p className="empty-chart">No hay datos para mostrar con esta selección.</p>
  }

  const values = items.map((item) => Number(item[valueKey] ?? 0))
  const maxValue = Math.max(...values, 1)

  return (
    <ol className="bar-list">
      {items.map((item) => {
        const value = Number(item[valueKey] ?? 0)
        const detail =
          item.detail ??
          (item.consoleCount !== undefined
            ? `${item.consoleCount} ${item.consoleCount === 1 ? 'consola' : 'consolas'}`
            : item.gameCount !== undefined
              ? `${item.gameCount} ${item.gameCount === 1 ? 'juego' : 'juegos'}`
              : null)

        return (
          <li className="bar-item" key={item.key ?? item.name}>
            <div className="bar-heading">
              <span>{item.name}</span>
              <strong>
                {formatNumber(value)}
                {unit}
              </strong>
            </div>
            <div
              className="bar-track"
              role="img"
              aria-label={`${item.name}: ${formatNumber(value)}${unit}`}
            >
              <span
                className={`bar-fill ${color}`}
                style={{ width: `${(value / maxValue) * 100}%` }}
              />
            </div>
            {detail && <span className="bar-detail">{detail}</span>}
          </li>
        )
      })}
    </ol>
  )
}

function TrendChart({ items }) {
  const [activePoint, setActivePoint] = useState(null)

  if (!items.length) {
    return <p className="empty-chart">No hay datos de ventas por año.</p>
  }

  const width = 720
  const height = 250
  const left = 44
  const right = 18
  const top = 18
  const bottom = 34
  const maxValue = Math.max(...items.map((item) => item.sales), 1)
  const points = items.map((item, index) => {
    const x =
      left +
      (items.length === 1 ? 0 : (index / (items.length - 1)) * (width - left - right))
    const y = top + ((maxValue - item.sales) / maxValue) * (height - top - bottom)
    return { ...item, x, y }
  })
  const labelsEvery = Math.max(1, Math.ceil(points.length / 8))
  const tooltipPosition = activePoint
    ? {
        left: `${Math.min(86, Math.max(14, (activePoint.x / width) * 100))}%`,
        top: `${Math.max(24, (activePoint.y / height) * 100)}%`,
      }
    : undefined

  return (
    <div className="trend-chart">
      <svg
        viewBox={`0 0 ${width} ${height}`}
        role="group"
        aria-label="Ventas de videojuegos por año de lanzamiento, en millones de copias"
      >
        {[0, 0.5, 1].map((ratio) => {
          const y = top + ratio * (height - top - bottom)
          return (
            <g key={ratio} className="trend-grid">
              <line x1={left} x2={width - right} y1={y} y2={y} />
              <text x={left - 8} y={y + 4} textAnchor="end">
                {formatNumber(maxValue * (1 - ratio))}
              </text>
            </g>
          )
        })}
        <polyline
          className="trend-line"
          points={points.map((point) => `${point.x},${point.y}`).join(' ')}
        />
        {points.map((point, index) => (
          <g key={point.releaseYear}>
            <circle
              className="trend-hit-area"
              cx={point.x}
              cy={point.y}
              r="9"
              tabIndex={0}
              aria-label={`Año ${point.releaseYear}: ${formatNumber(point.sales)} millones de copias`}
              onMouseEnter={() => setActivePoint(point)}
              onMouseLeave={() => setActivePoint(null)}
              onFocus={() => setActivePoint(point)}
              onBlur={() => setActivePoint(null)}
            >
              <title>
                Año {point.releaseYear}: {formatNumber(point.sales)} millones de copias
              </title>
            </circle>
            <circle
              className="trend-point"
              cx={point.x}
              cy={point.y}
              r="3"
              aria-hidden="true"
            />
            {(index % labelsEvery === 0 || index === points.length - 1) && (
              <text
                className="trend-year"
                x={point.x}
                y={height - 8}
                textAnchor="middle"
              >
                {point.releaseYear}
              </text>
            )}
          </g>
        ))}
      </svg>
      {activePoint && (
        <div
          className="trend-tooltip"
          role="tooltip"
          style={tooltipPosition}
        >
          <strong>{activePoint.releaseYear}</strong>
          <span>{formatNumber(activePoint.sales)} M de copias vendidas</span>
        </div>
      )}
      <p className="chart-hint">
        Pasa el cursor por un punto —o selecciónalo con Tab— para ver el año y
        las ventas exactas.
      </p>
    </div>
  )
}

function StatCard({ label, value, note, featured = false }) {
  return (
    <article className={`stat-card${featured ? ' featured' : ''}`}>
      <span className="stat-label">{label}</span>
      <strong className="stat-value">{value}</strong>
      <span className="stat-note">{note}</span>
    </article>
  )
}

function SectionHeading({ eyebrow, title, description }) {
  return (
    <div className="section-heading">
      <p className="eyebrow">{eyebrow}</p>
      <h2>{title}</h2>
      <p>{description}</p>
    </div>
  )
}

function FilterSelect({ label, name, value, options, onChange }) {
  return (
    <label className="filter-field">
      <span>{label}</span>
      <select name={name} value={value} onChange={onChange}>
        <option value="">Todos</option>
        {options.map((option) => (
          <option value={option.id} key={option.id}>
            {option.name}
          </option>
        ))}
      </select>
    </label>
  )
}

function Dashboard({
  hardware,
  catalogs,
  games,
  filters,
  filterError,
  onFilterChange,
  onApplyFilters,
  onResetFilters,
}) {
  const topConsole = hardware.consoles[0]
  const manufacturers = Array.from(
    new Map(
      hardware.consoles.map((item) => [
        item.manufacturerId,
        { id: item.manufacturerId, name: item.manufacturer },
      ]),
    ).values(),
  ).sort((a, b) => a.name.localeCompare(b.name))
  const generations = Array.from(
    new Map(
      hardware.consoles.map((item) => [
        item.generationId,
        { id: item.generationId, name: `Generación ${item.generation}` },
      ]),
    ).values(),
  ).sort((a, b) => a.name.localeCompare(b.name))
  const gameSummary = games.data?.summary
  const filteredResultsEmpty =
    games.status === 'success' && gameSummary?.gameCount === 0

  return (
    <>
      <header className="topbar">
        <a className="brand" href="/" aria-label="GameStats inicio">
          <span className="brand-mark">G</span>
          <span>GameStats</span>
        </a>
        <span className="data-badge">
          <span className="status-dot" />
          Datos reales de la base local
        </span>
      </header>

      <main className="dashboard">
        <section className="page-heading">
          <div>
            <p className="eyebrow">PANEL DE ESTADÍSTICAS</p>
            <h1>Consolas y videojuegos</h1>
            <p className="page-description">
              Estadísticas calculadas con los datos importados de hardware y
              videojuegos.
            </p>
          </div>
          <span className="updated-label">Ventas expresadas en millones</span>
        </section>

        <form className="filter-panel" onSubmit={onApplyFilters}>
          <div className="filter-heading">
            <div>
              <p className="eyebrow">EXPLORAR</p>
              <h2>Filtros de videojuegos</h2>
            </div>
            <span>Los gráficos de hardware no cambian con estos filtros.</span>
          </div>
          <div className="filter-grid">
            <label className="filter-field">
              <span>Año desde</span>
              <input
                name="yearFrom"
                type="number"
                min="1000"
                max="9999"
                value={filters.yearFrom}
                onChange={onFilterChange}
                placeholder="Ej. 1990"
              />
            </label>
            <label className="filter-field">
              <span>Año hasta</span>
              <input
                name="yearTo"
                type="number"
                min="1000"
                max="9999"
                value={filters.yearTo}
                onChange={onFilterChange}
                placeholder="Ej. 2020"
              />
            </label>
            <FilterSelect
              label="Generación"
              name="generationId"
              value={filters.generationId}
              options={generations}
              onChange={onFilterChange}
            />
            <FilterSelect
              label="Fabricante"
              name="manufacturerId"
              value={filters.manufacturerId}
              options={manufacturers}
              onChange={onFilterChange}
            />
            <FilterSelect
              label="Consola"
              name="consoleId"
              value={filters.consoleId}
              options={catalogs.consoles}
              onChange={onFilterChange}
            />
            <FilterSelect
              label="Publisher"
              name="publisherId"
              value={filters.publisherId}
              options={catalogs.publishers}
              onChange={onFilterChange}
            />
          </div>
          <div className="filter-actions">
            <p className="filter-error" role="alert">
              {filterError}
            </p>
            <div>
              <button className="secondary-button" type="button" onClick={onResetFilters}>
                Limpiar
              </button>
              <button className="primary-button" type="submit">
                Aplicar filtros
              </button>
            </div>
          </div>
        </form>

        <SectionHeading
          eyebrow="HARDWARE"
          title="Estadísticas de consolas"
          description="Ventas totales de consolas, agrupadas por fabricante y generación."
        />
        <section className="stats-grid" aria-label="Resumen de consolas">
          <StatCard
            label="Consolas registradas"
            value={formatNumber(hardware.summary.consoleCount)}
            note="en la base de datos"
          />
          <StatCard
            label="Ventas de hardware"
            value={`${formatNumber(hardware.summary.totalSales)} M`}
            note="unidades de consola"
          />
          <StatCard
            label="Fabricantes"
            value={formatNumber(hardware.summary.manufacturerCount)}
            note="con consolas registradas"
          />
          <StatCard
            label="Consola más vendida"
            value={topConsole?.name ?? 'Sin datos'}
            note={
              topConsole
                ? `${formatNumber(topConsole.sales)} M de unidades`
                : 'No hay ventas disponibles'
            }
            featured
          />
        </section>

        <section className="charts-grid" aria-label="Gráficos de consolas">
          <ChartCard
            eyebrow="RANKING"
            title="Consolas más vendidas"
            description="Ventas totales registradas, en millones de unidades."
            index="01"
            wide
          >
            <BarChart
              items={hardware.consoles.slice(0, 10).map((item) => ({
                name: item.name,
                sales: item.sales,
                detail: 'Ventas totales de hardware',
              }))}
            />
          </ChartCard>

          <ChartCard
            eyebrow="COMPARACIÓN"
            title="Ventas por fabricante"
            description="Suma de ventas de sus consolas."
            index="02"
          >
            <BarChart
              items={hardware.salesByManufacturer.map((item) => ({
                name: item.name,
                sales: item.sales,
                consoleCount: item.consoleCount,
              }))}
              color="purple"
            />
          </ChartCard>

          <ChartCard
            eyebrow="COMPARACIÓN"
            title="Ventas por generación"
            description="Suma de unidades de hardware por generación."
            index="03"
          >
            <BarChart
              items={hardware.salesByGeneration.map((item) => ({
                name: item.name,
                sales: item.sales,
                consoleCount: item.consoleCount,
              }))}
              color="green"
            />
          </ChartCard>

          <ChartCard
            eyebrow="LANZAMIENTOS"
            title="Consolas lanzadas por década"
            description="Cantidad según año de lanzamiento; no son ventas anuales."
            index="04"
            wide
          >
            <BarChart
              items={hardware.releasesByDecade.map((item) => ({
                name: item.decade,
                consoleCount: item.consoleCount,
              }))}
              valueKey="consoleCount"
              unit=""
              color="orange"
            />
          </ChartCard>
        </section>

        <SectionHeading
          eyebrow="SOFTWARE"
          title="Estadísticas de videojuegos"
          description="Consultas sobre ventas de juegos, publishers, desarrolladores y fabricantes."
        />
        {games.status === 'loading' && (
          <div className="inline-state" role="status">
            <span className="loading-spinner" />
            <span>Actualizando estadísticas de videojuegos...</span>
          </div>
        )}
        {games.status === 'error' && (
          <div className="inline-error" role="alert">
            No se pudieron cargar las estadísticas de videojuegos: {games.message}
          </div>
        )}
        {games.status === 'success' && (
          <>
            {filteredResultsEmpty && (
              <p className="empty-results" role="status">
                No hay videojuegos que coincidan con los filtros seleccionados.
              </p>
            )}
            <section className="stats-grid" aria-label="Resumen de videojuegos">
              <StatCard
                label="Videojuegos registrados"
                value={formatNumber(gameSummary.gameCount)}
                note="incluye juegos sin ventas reportadas"
              />
              <StatCard
                label="Ventas de videojuegos"
                value={`${formatNumber(gameSummary.totalSales)} M`}
                note="solo ventas informadas"
              />
              <StatCard
                label="Consola líder en juegos"
                value={gameSummary.topConsole?.name ?? 'Sin datos'}
                note={
                  gameSummary.topConsole
                    ? `${formatNumber(gameSummary.topConsole.sales)} M de copias`
                    : 'No hay ventas reportadas'
                }
                featured
              />
              <StatCard
                label="Generaciones con ventas"
                value={formatNumber(games.data.salesByGeneration.length)}
                note="de videojuegos reportadas"
              />
            </section>

            <section className="charts-grid" aria-label="Gráficos de videojuegos">
              <ChartCard
                eyebrow="RANKING"
                title="Videojuegos más vendidos"
                description="Los diez primeros según las ventas reportadas."
                index="05"
                wide
              >
                <BarChart
                  items={games.data.topGames.map((item) => ({
                    key: item.gameId,
                    name: item.title,
                    sales: item.sales,
                    detail: `${item.consoleName} · ${
                      item.releaseYear ?? 'Año no informado'
                    }`,
                  }))}
                />
              </ChartCard>

              <ChartCard
                eyebrow="PUBLISHERS"
                title="Ventas por publisher"
                description="Top diez; cantidad de juegos asociados."
                index="06"
              >
                <BarChart
                  items={games.data.publishers
                    .filter((item) => item.sales !== null)
                    .map((item) => ({
                      key: item.publisherId,
                      name: item.publisherName,
                      sales: item.sales,
                      gameCount: item.gameCount,
                    }))}
                  color="purple"
                />
              </ChartCard>

              <ChartCard
                eyebrow="DESARROLLADORES"
                title="Ventas por desarrollador"
                description="Top diez; cantidad de juegos asociados."
                index="07"
              >
                <BarChart
                  items={games.data.developers
                    .filter((item) => item.sales !== null)
                    .map((item) => ({
                      key: item.developerId,
                      name: item.developerName,
                      sales: item.sales,
                      gameCount: item.gameCount,
                    }))}
                  color="green"
                />
              </ChartCard>

              <ChartCard
                eyebrow="EVOLUCIÓN"
                title="Ventas de juegos por año"
                description="Agrupadas por año de lanzamiento del videojuego."
                index="08"
                wide
              >
                <TrendChart items={games.data.years} />
              </ChartCard>

              <ChartCard
                eyebrow="COMPARACIÓN"
                title="Ventas de juegos por consola"
                description="Suma de ventas reportadas por consola."
                index="09"
              >
                <BarChart
                  items={games.data.salesByConsole.slice(0, 10).map((item) => ({
                    key: item.consoleId,
                    name: item.consoleName,
                    sales: item.sales,
                  }))}
                  color="orange"
                />
              </ChartCard>

              <ChartCard
                eyebrow="COMPARACIÓN"
                title="Ventas de juegos por generación"
                description="Suma de ventas reportadas por generación."
                index="10"
              >
                <BarChart
                  items={games.data.salesByGeneration.map((item) => ({
                    key: item.generationId,
                    name: `Generación ${item.generationNumber}`,
                    sales: item.sales,
                  }))}
                  color="blue"
                />
              </ChartCard>

              <ChartCard
                eyebrow="COMPARACIÓN"
                title="Ventas de juegos por fabricante"
                description="Fabricante de la consola asociada a cada juego."
                index="11"
              >
                <BarChart
                  items={games.data.salesByManufacturer.map((item) => ({
                    key: item.manufacturerId,
                    name: item.manufacturerName,
                    sales: item.sales,
                  }))}
                  color="purple"
                />
              </ChartCard>

              <ChartCard
                eyebrow="LIDERAZGO"
                title="Fabricante dominante por generación"
                description="El fabricante con más ventas de videojuegos en cada generación."
                index="12"
              >
                <BarChart
                  items={games.data.dominantManufacturers.map((item) => ({
                    key: item.generationId,
                    name: `Generación ${item.generationNumber} · ${item.manufacturer.name}`,
                    sales: item.sales,
                  }))}
                  color="green"
                />
              </ChartCard>
            </section>
          </>
        )}

        <p className="data-note">
          Las ventas de videojuegos usan la unidad del CSV (millones de copias);
          los valores faltantes no se suman. Los juegos sin ventas o fecha pueden
          aparecer en el total de registros, pero no en gráficos que requieren
          esos datos.
        </p>
      </main>
      <footer className="footer">
        GameStats <span>•</span> Panel de consolas y videojuegos
      </footer>
    </>
  )
}

function App() {
  const [base, setBase] = useState({ status: 'loading', data: null })
  const [games, setGames] = useState({ status: 'loading', data: null })
  const [filters, setFilters] = useState(initialFilters)
  const [appliedFilters, setAppliedFilters] = useState(initialFilters)
  const [filterError, setFilterError] = useState('')

  useEffect(() => {
    const controller = new AbortController()

    async function loadBaseData() {
      try {
        const [hardware, consoles, publishers] = await Promise.all([
          requestJson('/api/estadisticas/consolas', controller.signal),
          requestItems('/api/consolas', controller.signal),
          requestItems('/api/publishers', controller.signal),
        ])
        setBase({
          status: 'success',
          data: { hardware, catalogs: { consoles, publishers } },
        })
      } catch (error) {
        if (error.name !== 'AbortError') {
          setBase({ status: 'error', data: null, message: error.message })
        }
      }
    }

    loadBaseData()
    return () => controller.abort()
  }, [])

  useEffect(() => {
    if (base.status !== 'success') {
      return undefined
    }

    const controller = new AbortController()

    async function loadGameStatistics() {
      try {
        const results = await Promise.all(
          Object.entries(gameEndpoints).map(([key, endpoint]) =>
            requestJson(withFilters(endpoint, appliedFilters), controller.signal).then(
              (data) => [key, data],
            ),
          ),
        )
        setGames({
          status: 'success',
          data: Object.fromEntries(results),
        })
      } catch (error) {
        if (error.name !== 'AbortError') {
          setGames({ status: 'error', data: null, message: error.message })
        }
      }
    }

    loadGameStatistics()
    return () => controller.abort()
  }, [base.status, appliedFilters])

  function handleFilterChange(event) {
    const { name, value } = event.target
    setFilters((current) => ({ ...current, [name]: value }))
  }

  function applyFilters(event) {
    event.preventDefault()
    if (
      filters.yearFrom &&
      filters.yearTo &&
      Number(filters.yearFrom) > Number(filters.yearTo)
    ) {
      setFilterError('El año desde no puede ser mayor que el año hasta.')
      return
    }
    setFilterError('')
    setGames({ status: 'loading', data: null })
    setAppliedFilters({ ...filters })
  }

  function resetFilters() {
    setFilters({ ...initialFilters })
    setGames({ status: 'loading', data: null })
    setAppliedFilters({ ...initialFilters })
    setFilterError('')
  }

  if (base.status === 'loading') {
    return (
      <main className="state-screen">
        <div className="state-card" role="status">
          <span className="loading-spinner" />
          <h1>Cargando estadísticas</h1>
          <p>Conectando con la base local de consolas y videojuegos...</p>
        </div>
      </main>
    )
  }

  if (base.status === 'error') {
    return (
      <main className="state-screen">
        <div className="state-card" role="alert">
          <span className="error-icon">!</span>
          <h1>No se pudieron cargar los datos</h1>
          <p>{base.message}</p>
          <p className="state-hint">
            Verifica que el backend esté ejecutándose y vuelve a cargar la página.
          </p>
        </div>
      </main>
    )
  }

  return (
    <Dashboard
      hardware={base.data.hardware}
      catalogs={base.data.catalogs}
      games={games}
      filters={filters}
      filterError={filterError}
      onFilterChange={handleFilterChange}
      onApplyFilters={applyFilters}
      onResetFilters={resetFilters}
    />
  )
}

export default App
