import { useEffect, useState } from 'react'

import {
  gameEndpoints,
  initialFilters,
  requestCatalogItems,
  requestStatistics,
  withFilters,
} from '../../api/estadisticas'
import {
  BarChart,
  ChartCard,
  FilterSelect,
  SectionHeading,
  StatCard,
  TrendChart,
} from './StatisticsComponents'
import formatNumber from '../../utils/formatNumber'

function uniqueOptions(items, idKey, nameKey, namePrefix = '') {
  return Array.from(
    new Map(
      items.map((item) => [
        item[idKey],
        { id: item[idKey], name: `${namePrefix}${item[nameKey]}` },
      ]),
    ).values(),
  ).sort((a, b) => a.name.localeCompare(b.name))
}

export default function VideojuegosTab() {
  const [catalogs, setCatalogs] = useState({ status: 'loading', data: null })
  const [games, setGames] = useState({ status: 'loading', data: null })
  const [filters, setFilters] = useState(initialFilters)
  const [appliedFilters, setAppliedFilters] = useState(initialFilters)
  const [filterError, setFilterError] = useState('')

  useEffect(() => {
    const controller = new AbortController()

    async function loadFilterOptions() {
      try {
        const [hardware, consoles, publishers, developers] = await Promise.all([
          requestStatistics('/api/estadisticas/consolas', controller.signal),
          requestCatalogItems('/api/consolas', controller.signal),
          requestCatalogItems('/api/publishers', controller.signal),
          requestCatalogItems('/api/desarrolladores', controller.signal),
        ])
        setCatalogs({
          status: 'success',
          data: { hardware, consoles, publishers, developers },
        })
      } catch (error) {
        if (error.name !== 'AbortError') {
          setCatalogs({ status: 'error', data: null, message: error.message })
        }
      }
    }

    loadFilterOptions()
    return () => controller.abort()
  }, [])

  useEffect(() => {
    const controller = new AbortController()

    async function loadGameStatistics() {
      setGames({ status: 'loading', data: null })
      try {
        const results = await Promise.all(
          Object.entries(gameEndpoints).map(([key, endpoint]) =>
            requestStatistics(
              withFilters(endpoint, appliedFilters),
              controller.signal,
            ).then((data) => [key, data]),
          ),
        )
        setGames({ status: 'success', data: Object.fromEntries(results) })
      } catch (error) {
        if (error.name !== 'AbortError') {
          setGames({ status: 'error', data: null, message: error.message })
        }
      }
    }

    loadGameStatistics()
    return () => controller.abort()
  }, [appliedFilters])

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
    setAppliedFilters({ ...filters })
  }

  function resetFilters() {
    setFilters({ ...initialFilters })
    setAppliedFilters({ ...initialFilters })
    setFilterError('')
  }

  const hardwareConsoles = catalogs.data?.hardware.consoles ?? []
  const manufacturers = uniqueOptions(
    hardwareConsoles,
    'manufacturerId',
    'manufacturer',
  )
  const generations = uniqueOptions(
    hardwareConsoles,
    'generationId',
    'generation',
    'Generación ',
  )
  const gameSummary = games.data?.summary
  const filteredResultsEmpty =
    games.status === 'success' && gameSummary?.gameCount === 0

  return (
    <>
      <SectionHeading
        eyebrow="SOFTWARE"
        title="Estadísticas de videojuegos"
        description="Filtra las ventas y métricas de los videojuegos."
      />

      <form className="filter-panel" onSubmit={applyFilters}>
        <div className="filter-heading">
          <div>
            <p className="eyebrow">EXPLORAR</p>
            <h2>Filtros de videojuegos</h2>
          </div>
        </div>
        <div className="filter-grid">
          <FilterSelect
            label="Fabricante"
            name="manufacturerId"
            value={filters.manufacturerId}
            options={manufacturers}
            onChange={handleFilterChange}
          />
          <FilterSelect
            label="Consola"
            name="consoleId"
            value={filters.consoleId}
            options={catalogs.data?.consoles ?? []}
            onChange={handleFilterChange}
          />
          <FilterSelect
            label="Publisher"
            name="publisherId"
            value={filters.publisherId}
            options={catalogs.data?.publishers ?? []}
            onChange={handleFilterChange}
          />
          <FilterSelect
            label="Desarrollador"
            name="developerId"
            value={filters.developerId}
            options={catalogs.data?.developers ?? []}
            onChange={handleFilterChange}
          />
          <label className="filter-field">
            <span>Año desde</span>
            <input
              name="yearFrom"
              type="number"
              min="1000"
              max="9999"
              value={filters.yearFrom}
              onChange={handleFilterChange}
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
              onChange={handleFilterChange}
              placeholder="Ej. 2020"
            />
          </label>
          <FilterSelect
            label="Generación"
            name="generationId"
            value={filters.generationId}
            options={generations}
            onChange={handleFilterChange}
          />
        </div>
        {catalogs.status === 'error' && (
          <p className="inline-error" role="alert">
            No se pudieron cargar las opciones de filtro: {catalogs.message}
          </p>
        )}
        <div className="filter-actions">
          <p className="filter-error" role="alert">
            {filterError}
          </p>
          <div>
            <button
              className="secondary-button"
              type="button"
              onClick={resetFilters}
            >
              Limpiar
            </button>
            <button className="primary-button" type="submit">
              Aplicar filtros
            </button>
          </div>
        </div>
      </form>

      {games.status === 'loading' && (
        <div className="inline-state" role="status">
          <span className="loading-spinner" />
          <span>Cargando estadísticas de videojuegos...</span>
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
              index="01"
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
              index="02"
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
              index="03"
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
              index="04"
              wide
            >
              <TrendChart items={games.data.years} />
            </ChartCard>

            <ChartCard
              eyebrow="COMPARACIÓN"
              title="Ventas de juegos por consola"
              description="Suma de ventas reportadas por consola."
              index="05"
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
              index="06"
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
              index="07"
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
              index="08"
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
          <p className="data-note">
            Las ventas de videojuegos usan la unidad del CSV (millones de
            copias); los valores faltantes no se suman. Los juegos sin ventas o
            fecha pueden aparecer en el total, pero no en gráficos que requieren
            esos datos.
          </p>
        </>
      )}
    </>
  )
}
