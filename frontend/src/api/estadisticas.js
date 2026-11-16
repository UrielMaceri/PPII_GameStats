import { getAuthHeaders } from '../auth/session'

export const initialFilters = {
  yearFrom: '',
  yearTo: '',
  generationId: '',
  manufacturerId: '',
  consoleId: '',
  publisherId: '',
  developerId: '',
}

export const gameEndpoints = {
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

export async function requestStatistics(path, signal) {
  const response = await fetch(path, {
    signal,
    headers: getAuthHeaders(),
  })
  if (!response.ok) {
    throw new Error(`La API respondió con estado ${response.status}.`)
  }

  const result = await response.json()
  if (result.data === undefined || result.meta === undefined) {
    throw new Error('La respuesta de estadísticas tiene un formato inválido.')
  }
  return result.data
}

export async function requestCatalogItems(path, signal) {
  const response = await fetch(path, {
    signal,
    headers: getAuthHeaders(),
  })
  if (!response.ok) {
    throw new Error(`La API respondió con estado ${response.status}.`)
  }

  const result = await response.json()
  if (!Array.isArray(result.data)) {
    throw new Error('La respuesta del catálogo tiene un formato inválido.')
  }
  return result.data
}

export function withFilters(endpoint, filters) {
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
