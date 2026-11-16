import { useState } from 'react'

import formatNumber from '../../utils/formatNumber'

export function StatisticsStatus({ status, message, loadingMessage }) {
  if (status === 'loading') {
    return (
      <div className="state-screen statistics-state">
        <div className="state-card" role="status">
          <span className="loading-spinner" />
          <h1>Cargando estadísticas</h1>
          <p>{loadingMessage}</p>
        </div>
      </div>
    )
  }

  if (status === 'error') {
    return (
      <div className="state-screen statistics-state">
        <div className="state-card" role="alert">
          <span className="error-icon">!</span>
          <h1>No se pudieron cargar los datos</h1>
          <p>{message}</p>
          <p className="state-hint">
            Verifica que el backend esté ejecutándose y vuelve a intentarlo.
          </p>
        </div>
      </div>
    )
  }

  return null
}

export function ChartCard({
  eyebrow,
  title,
  description,
  index,
  wide = false,
  children,
}) {
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

export function BarChart({
  items,
  valueKey = 'sales',
  unit = ' M',
  color = 'blue',
}) {
  if (!items.length) {
    return (
      <p className="empty-chart">
        No hay datos para mostrar con esta selección.
      </p>
    )
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

export function TrendChart({ items }) {
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
      (items.length === 1
        ? 0
        : (index / (items.length - 1)) * (width - left - right))
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

export function StatCard({ label, value, note, featured = false }) {
  return (
    <article className={`stat-card${featured ? ' featured' : ''}`}>
      <span className="stat-label">{label}</span>
      <strong className="stat-value">{value}</strong>
      <span className="stat-note">{note}</span>
    </article>
  )
}

export function SectionHeading({ eyebrow, title, description }) {
  return (
    <div className="section-heading">
      <p className="eyebrow">{eyebrow}</p>
      <h2>{title}</h2>
      <p>{description}</p>
    </div>
  )
}

export function FilterSelect({ label, name, value, options, onChange }) {
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
