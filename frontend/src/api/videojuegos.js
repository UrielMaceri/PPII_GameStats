class ApiError extends Error {
  constructor(status, error) {
    super(error?.message ?? `La API respondió con estado ${status}.`)
    this.name = 'ApiError'
    this.status = status
    this.code = error?.code
    this.details = Array.isArray(error?.details) ? error.details : []
  }
}

async function request(path, options = {}) {
  let response
  try {
    response = await fetch(path, options)
  } catch (error) {
    if (error.name === 'AbortError') {
      throw error
    }
    throw new Error('No se pudo conectar con el servidor.', { cause: error })
  }

  if (response.status === 204) {
    return null
  }

  const result = await response.json()
  if (!response.ok) {
    throw new ApiError(response.status, result?.error)
  }
  return result
}

export async function listVideojuegos(params, signal) {
  const query = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value !== '' && value !== null && value !== undefined) {
      query.set(key, value)
    }
  })

  const result = await request(`/api/videojuegos?${query.toString()}`, { signal })
  if (!Array.isArray(result?.data) || !result.pagination) {
    throw new Error('La respuesta del catálogo tiene un formato inválido.')
  }
  return result
}

export async function loadVideojuegoOptions(signal) {
  const [consoles, publishers, developers] = await Promise.all([
    request('/api/consolas', { signal }),
    request('/api/publishers', { signal }),
    request('/api/desarrolladores', { signal }),
  ])
  for (const [label, result] of [
    ['consolas', consoles],
    ['publishers', publishers],
    ['desarrolladores', developers],
  ]) {
    if (!Array.isArray(result?.data)) {
      throw new Error(`La respuesta de ${label} tiene un formato inválido.`)
    }
  }
  return {
    consoles: consoles.data,
    publishers: publishers.data,
    developers: developers.data,
  }
}

export async function createVideojuego(data) {
  return request('/api/videojuegos', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
}

export async function updateVideojuego(id, data) {
  return request(`/api/videojuegos/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
}

export async function deleteVideojuego(id) {
  return request(`/api/videojuegos/${id}`, { method: 'DELETE' })
}
