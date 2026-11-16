import { useEffect, useRef, useState } from 'react'

import {
  createVideojuego,
  deleteVideojuego,
  listVideojuegos,
  loadVideojuegoOptions,
  updateVideojuego,
} from '../../api/videojuegos'
import formatNumber from '../../utils/formatNumber'

const PAGE_SIZE = 20
const initialFilters = {
  search: '',
  consoleId: '',
  publisherId: '',
  developerId: '',
  yearFrom: '',
  yearTo: '',
}
const emptyForm = {
  title: '',
  consoleId: '',
  publisherId: '',
  developerId: '',
  releaseYear: '',
  sales: '',
}
function SearchableCatalogSelect({
  label,
  name,
  options,
  value,
  onChange,
  required = false,
  disabled = false,
  error,
  compact = false,
}) {
  const [search, setSearch] = useState('')
  const normalizedSearch = search.trim().toLocaleLowerCase()
  const matchingOptions = normalizedSearch
    ? options.filter((option) =>
        option.name.toLocaleLowerCase().includes(normalizedSearch),
      )
    : options
  let visibleOptions = matchingOptions
  const selectedOption = options.find((option) => String(option.id) === value)
  if (
    selectedOption &&
    !visibleOptions.some((option) => String(option.id) === value)
  ) {
    visibleOptions = [selectedOption, ...visibleOptions]
  }

  const selectId = `${compact ? 'filter' : 'game'}-${name}`
  const errorId = `${selectId}-error`

  return (
    <div
      className={
        compact
          ? 'filter-field filter-catalog-select'
          : 'game-form-field catalog-select-field'
      }
    >
      <label htmlFor={selectId}>{label}{required && ' *'}</label>
      <input
        type="search"
        value={search}
        onChange={(event) => setSearch(event.target.value)}
        placeholder={`Buscar ${label.toLocaleLowerCase()}...`}
        aria-label={`Buscar ${label.toLocaleLowerCase()}`}
        disabled={disabled}
      />
      <select
        id={selectId}
        name={name}
        value={value}
        onChange={onChange}
        required={required}
        disabled={disabled}
        aria-invalid={Boolean(error)}
        aria-describedby={error ? errorId : undefined}
      >
        <option value="">
          {required ? 'Selecciona una opción' : 'Sin asignar'}
        </option>
        {visibleOptions.map((option) => (
          <option value={option.id} key={option.id}>
            {option.name}
          </option>
        ))}
      </select>
      {matchingOptions.length === 0 && search && (
        <span className="field-hint">No hay coincidencias.</span>
      )}
      {error && (
        <span className="field-error" id={errorId}>
          {error}
        </span>
      )}
    </div>
  )
}

function getFieldErrors(error) {
  return Object.fromEntries(
    (error.details ?? [])
      .filter((detail) => detail.field)
      .map((detail) => [detail.field, detail.message]),
  )
}

export default function VideojuegosTab() {
  const [listState, setListState] = useState({
    status: 'loading',
    items: [],
    pagination: null,
  })
  const [optionsState, setOptionsState] = useState({
    status: 'loading',
    data: null,
    message: '',
  })
  const [filters, setFilters] = useState(initialFilters)
  const [appliedFilters, setAppliedFilters] = useState(initialFilters)
  const [page, setPage] = useState(1)
  const [reloadKey, setReloadKey] = useState(0)
  const [formMode, setFormMode] = useState(null)
  const [editingId, setEditingId] = useState(null)
  const [form, setForm] = useState(emptyForm)
  const [formErrors, setFormErrors] = useState({})
  const [formMessage, setFormMessage] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [notice, setNotice] = useState('')
  const [actionError, setActionError] = useState('')
  const [filterError, setFilterError] = useState('')
  const formDialogRef = useRef(null)

  useEffect(() => {
    const controller = new AbortController()

    async function loadOptions() {
      try {
        const data = await loadVideojuegoOptions(controller.signal)
        setOptionsState({ status: 'success', data, message: '' })
      } catch (error) {
        if (error.name !== 'AbortError') {
          setOptionsState({
            status: 'error',
            data: null,
            message: error.message,
          })
        }
      }
    }

    loadOptions()
    return () => controller.abort()
  }, [])

  useEffect(() => {
    const controller = new AbortController()

    async function loadGames() {
      setListState({ status: 'loading', items: [], pagination: null })
      try {
        const result = await listVideojuegos(
          { page, pageSize: PAGE_SIZE, ...appliedFilters },
          controller.signal,
        )
        setListState({
          status: 'success',
          items: result.data,
          pagination: result.pagination,
        })
      } catch (error) {
        if (error.name !== 'AbortError') {
          setListState({
            status: 'error',
            items: [],
            pagination: null,
            message: error.message,
          })
        }
      }
    }

    loadGames()
    return () => controller.abort()
  }, [appliedFilters, page, reloadKey])

  useEffect(() => {
    const dialog = formDialogRef.current
    if (formMode && dialog && !dialog.open) {
      dialog.showModal()
    } else if (!formMode && dialog?.open) {
      dialog.close()
    }
  }, [formMode])

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
    setNotice('')
    setActionError('')
    setPage(1)
    setAppliedFilters({ ...filters })
  }

  function clearFilters() {
    setFilters({ ...initialFilters })
    setAppliedFilters({ ...initialFilters })
    setFilterError('')
    setPage(1)
  }

  function startCreate() {
    setEditingId(null)
    setForm({ ...emptyForm })
    setFormErrors({})
    setFormMessage('')
    setActionError('')
    setNotice('')
    setFormMode('create')
  }

  function startEdit(videojuego) {
    setEditingId(videojuego.id)
    setForm({
      title: videojuego.title,
      consoleId: String(videojuego.console.id),
      publisherId: videojuego.publisher
        ? String(videojuego.publisher.id)
        : '',
      developerId: videojuego.developer
        ? String(videojuego.developer.id)
        : '',
      releaseYear:
        videojuego.releaseYear === null
          ? ''
          : String(videojuego.releaseYear),
      sales: videojuego.sales === null ? '' : String(videojuego.sales),
    })
    setFormErrors({})
    setFormMessage('')
    setActionError('')
    setNotice('')
    setFormMode('edit')
  }

  function closeForm() {
    setFormMode(null)
    setEditingId(null)
    setFormErrors({})
    setFormMessage('')
  }

  function handleDialogKeyDown(event) {
    if (event.key === 'Escape') {
      event.preventDefault()
      if (!submitting) {
        closeForm()
      }
    }
  }

  function handleFormCancel(event) {
    event.preventDefault()
    if (!submitting) {
      closeForm()
    }
  }

  function handleDialogClick(event) {
    if (event.target === event.currentTarget && !submitting) {
      closeForm()
    }
  }

  function handleFormChange(event) {
    const { name, value } = event.target
    setForm((current) => ({ ...current, [name]: value }))
    setFormErrors((current) => ({ ...current, [name]: '' }))
    setFormMessage('')
  }

  async function submitForm(event) {
    event.preventDefault()
    const payload = {
      title: form.title,
      consoleId: Number(form.consoleId),
      publisherId: form.publisherId ? Number(form.publisherId) : null,
      developerId: form.developerId ? Number(form.developerId) : null,
      releaseYear: form.releaseYear ? Number(form.releaseYear) : null,
      sales: form.sales ? Number(form.sales) : null,
    }

    setSubmitting(true)
    setFormErrors({})
    setFormMessage('')
    try {
      if (formMode === 'edit') {
        await updateVideojuego(editingId, payload)
      } else {
        await createVideojuego(payload)
      }

      const wasCreating = formMode === 'create'
      closeForm()
      setNotice(
        wasCreating
          ? 'El videojuego se creó correctamente.'
          : 'Los cambios se guardaron correctamente.',
      )
      setActionError('')
      if (wasCreating) {
        setFilters({ ...initialFilters })
        setAppliedFilters({ ...initialFilters })
        setPage(1)
      }
      setReloadKey((current) => current + 1)
    } catch (error) {
      setFormErrors(getFieldErrors(error))
      setFormMessage(error.message)
    } finally {
      setSubmitting(false)
    }
  }

  async function removeVideojuego(videojuego) {
    const confirmed = window.confirm(
      `¿Eliminar "${videojuego.title}"? Esta acción no se puede deshacer.`,
    )
    if (!confirmed) {
      return
    }

    setNotice('')
    setActionError('')
    try {
      await deleteVideojuego(videojuego.id)
      setNotice(`Se eliminó "${videojuego.title}".`)
      if (listState.items.length === 1 && page > 1) {
        setPage((current) => current - 1)
      } else {
        setReloadKey((current) => current + 1)
      }
    } catch (error) {
      setActionError(error.message)
    }
  }

  const options = optionsState.data
  const pagination = listState.pagination
  const totalPages = Math.max(pagination?.totalPages ?? 0, 1)
  const firstItem =
    pagination && pagination.totalItems > 0
      ? (pagination.page - 1) * pagination.pageSize + 1
      : 0
  const lastItem =
    pagination && pagination.totalItems > 0
      ? firstItem + listState.items.length - 1
      : 0

  return (
    <>
      <section className="abm-toolbar" aria-label="Acciones del catálogo">
        <div>
          <h2>Videojuegos</h2>
          <p>Busca, filtra y administra los registros del catálogo.</p>
        </div>
        <button
          className="primary-button"
          type="button"
          onClick={startCreate}
          disabled={optionsState.status !== 'success'}
        >
          {optionsState.status === 'loading'
            ? 'Cargando opciones...'
            : 'Nuevo videojuego'}
        </button>
      </section>

      {optionsState.status === 'error' && (
        <div className="inline-error" role="alert">
          No se pudieron cargar las opciones de consolas, publishers y
          desarrolladores: {optionsState.message}
        </div>
      )}
      {notice && (
        <p className="abm-notice" role="status">
          {notice}
        </p>
      )}
      {actionError && (
        <p className="inline-error" role="alert">
          {actionError}
        </p>
      )}

      <dialog
        className="game-modal"
        ref={formDialogRef}
        onCancel={handleFormCancel}
        onKeyDown={handleDialogKeyDown}
        onClick={handleDialogClick}
        aria-labelledby="game-form-heading"
      >
        {formMode && options && (
          <section className="game-form-panel">
            <div className="form-panel-heading">
              <div>
                <p className="eyebrow">
                  {formMode === 'create' ? 'ALTA' : 'EDICIÓN'}
                </p>
                <h2 id="game-form-heading">
                  {formMode === 'create'
                    ? 'Nuevo videojuego'
                    : 'Editar videojuego'}
                </h2>
              </div>
              <button
                className="secondary-button"
                type="button"
                onClick={closeForm}
                disabled={submitting}
              >
                Cancelar
              </button>
            </div>

            <form className="game-form" onSubmit={submitForm}>
              <div className="game-form-field">
                <label htmlFor="game-title">Título *</label>
                <input
                  id="game-title"
                  name="title"
                  type="text"
                  maxLength={255}
                  value={form.title}
                  onChange={handleFormChange}
                  required
                  autoFocus
                  aria-invalid={Boolean(formErrors.title)}
                  aria-describedby={
                    formErrors.title ? 'game-title-error' : undefined
                  }
                />
                {formErrors.title && (
                  <span className="field-error" id="game-title-error">
                    {formErrors.title}
                  </span>
                )}
              </div>

              <SearchableCatalogSelect
                label="Consola"
                name="consoleId"
                options={options.consoles}
                value={form.consoleId}
                onChange={handleFormChange}
                required
                error={formErrors.consoleId}
              />
              <SearchableCatalogSelect
                label="Publisher"
                name="publisherId"
                options={options.publishers}
                value={form.publisherId}
                onChange={handleFormChange}
                error={formErrors.publisherId}
              />
              <SearchableCatalogSelect
                label="Desarrollador"
                name="developerId"
                options={options.developers}
                value={form.developerId}
                onChange={handleFormChange}
                error={formErrors.developerId}
              />

              <div className="game-form-field">
                <label htmlFor="game-release-year">Año de lanzamiento</label>
                <input
                  id="game-release-year"
                  name="releaseYear"
                  type="number"
                  min="1000"
                  max="9999"
                  step="1"
                  value={form.releaseYear}
                  onChange={handleFormChange}
                  aria-invalid={Boolean(formErrors.releaseYear)}
                  aria-describedby={
                    formErrors.releaseYear
                      ? 'game-release-year-error'
                      : undefined
                  }
                />
                {formErrors.releaseYear && (
                  <span className="field-error" id="game-release-year-error">
                    {formErrors.releaseYear}
                  </span>
                )}
              </div>

              <div className="game-form-field">
                <label htmlFor="game-sales">Ventas (millones de copias)</label>
                <input
                  id="game-sales"
                  name="sales"
                  type="number"
                  min="0"
                  step="any"
                  value={form.sales}
                  onChange={handleFormChange}
                  aria-invalid={Boolean(formErrors.sales)}
                  aria-describedby={
                    formErrors.sales ? 'game-sales-error' : undefined
                  }
                />
                {formErrors.sales && (
                  <span className="field-error" id="game-sales-error">
                    {formErrors.sales}
                  </span>
                )}
              </div>

              {formMessage && (
                <p className="inline-error form-error" role="alert">
                  {formMessage}
                </p>
              )}
              <div className="form-actions">
                <button
                  className="secondary-button"
                  type="button"
                  onClick={closeForm}
                  disabled={submitting}
                >
                  Cancelar
                </button>
                <button
                  className="primary-button"
                  type="submit"
                  disabled={submitting}
                >
                  {submitting
                    ? 'Guardando...'
                    : formMode === 'create'
                      ? 'Crear videojuego'
                      : 'Guardar cambios'}
                </button>
              </div>
            </form>
          </section>
        )}
      </dialog>

      <form className="filter-panel game-filter-panel" onSubmit={applyFilters}>
        <div className="filter-heading">
          <div>
            <p className="eyebrow">BUSCAR EN EL CATÁLOGO</p>
            <h2>Filtros</h2>
          </div>
        </div>
        <div className="game-filter-grid">
          <label className="filter-field game-search-field">
            <span>Título</span>
            <input
              name="search"
              type="search"
              maxLength={255}
              value={filters.search}
              onChange={handleFilterChange}
              placeholder="Buscar por título..."
            />
          </label>
          <label className="filter-field">
            <span>Consola</span>
            <select
              name="consoleId"
              value={filters.consoleId}
              onChange={handleFilterChange}
            >
              <option value="">Todas</option>
              {(options?.consoles ?? []).map((item) => (
                <option value={item.id} key={item.id}>
                  {item.name}
                </option>
              ))}
            </select>
          </label>
          <SearchableCatalogSelect
            compact
            label="Publisher"
            name="publisherId"
            options={options?.publishers ?? []}
            value={filters.publisherId}
            onChange={handleFilterChange}
          />
          <SearchableCatalogSelect
            compact
            label="Desarrollador"
            name="developerId"
            options={options?.developers ?? []}
            value={filters.developerId}
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
            />
          </label>
        </div>
        {filterError && (
          <p className="filter-error" role="alert">
            {filterError}
          </p>
        )}
        <div className="filter-actions">
          <span />
          <div>
            <button
              className="secondary-button"
              type="button"
              onClick={clearFilters}
            >
              Limpiar
            </button>
            <button className="primary-button" type="submit">
              Aplicar filtros
            </button>
          </div>
        </div>
      </form>

      <section className="game-list-panel" aria-labelledby="game-list-heading">
        <div className="game-list-heading">
          <div>
            <h2 id="game-list-heading">Videojuegos del catálogo</h2>
            {listState.status === 'success' && (
              <p>
                {pagination.totalItems === 0
                  ? '0 resultados'
                  : `Mostrando ${firstItem}–${lastItem} de ${pagination.totalItems}`}
              </p>
            )}
          </div>
        </div>

        {listState.status === 'loading' && (
          <div className="inline-state" role="status">
            <span className="loading-spinner" />
            <span>Cargando videojuegos...</span>
          </div>
        )}
        {listState.status === 'error' && (
          <p className="inline-error" role="alert">
            No se pudo cargar el catálogo: {listState.message}
          </p>
        )}
        {listState.status === 'success' && listState.items.length === 0 && (
          <p className="empty-results" role="status">
            No hay videojuegos que coincidan con la búsqueda.
          </p>
        )}
        {listState.status === 'success' && listState.items.length > 0 && (
          <>
            <div className="game-table-scroll">
              <table className="game-table">
                <thead>
                  <tr>
                    <th scope="col">Título</th>
                    <th scope="col">Consola</th>
                    <th scope="col">Publisher</th>
                    <th scope="col">Desarrollador</th>
                    <th scope="col">Año</th>
                    <th scope="col">Ventas (M)</th>
                    <th scope="col">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {listState.items.map((videojuego) => (
                    <tr key={videojuego.id}>
                      <td className="game-title-cell">{videojuego.title}</td>
                      <td>{videojuego.console.name}</td>
                      <td>{videojuego.publisher?.name ?? '—'}</td>
                      <td>{videojuego.developer?.name ?? '—'}</td>
                      <td>{videojuego.releaseYear ?? '—'}</td>
                      <td>
                        {videojuego.sales === null
                          ? '—'
                          : formatNumber(videojuego.sales)}
                      </td>
                      <td>
                        <div className="game-row-actions">
                          <button
                            className="text-button"
                            type="button"
                            onClick={() => startEdit(videojuego)}
                            disabled={optionsState.status !== 'success'}
                          >
                            Editar
                          </button>
                          <button
                            className="text-button danger"
                            type="button"
                            onClick={() => removeVideojuego(videojuego)}
                          >
                            Eliminar
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="game-pagination">
              <span>
                Página {pagination.page} de {totalPages}
              </span>
              <div>
                <button
                  className="secondary-button"
                  type="button"
                  onClick={() => setPage((current) => current - 1)}
                  disabled={page <= 1}
                >
                  Anterior
                </button>
                <button
                  className="secondary-button"
                  type="button"
                  onClick={() => setPage((current) => current + 1)}
                  disabled={page >= totalPages}
                >
                  Siguiente
                </button>
              </div>
            </div>
          </>
        )}
      </section>
    </>
  )
}
