# Frontend de GameStats

Aplicación React con Vite y React Router. Las rutas principales son `/`,
`/estadisticas` y `/abm`; `/estadistica` redirige a `/estadisticas`.

## Estructura

- `src/App.jsx`: router y menú principal.
- `src/pages/Estadisticas.jsx`: navegación por pestañas de estadísticas.
- `src/components/estadisticas/ConsolasTab.jsx`: estadísticas de consolas, sin
  filtros.
- `src/components/estadisticas/VideojuegosTab.jsx`: estadísticas de videojuegos
  y filtros.
- `src/components/estadisticas/StatisticsComponents.jsx`: gráficos y
  componentes visuales compartidos.
- `src/pages/ABM.jsx`: pantalla de administración con pestañas de catálogo.
- `src/components/abm/VideojuegosTab.jsx`: listado, filtros, formulario y
  operaciones de videojuegos.
- `src/api/estadisticas.js`: llamadas y utilidades para las respuestas de la
  API de estadísticas.
- `src/api/videojuegos.js`: llamadas CRUD y de catálogo auxiliar para el ABM.

La pestaña de consolas consulta sus datos al abrirse. La de videojuegos aplica
los filtros al consultar las estadísticas de juegos; la información de
hardware se solicita únicamente para poblar las opciones de fabricante y
generación.

La pestaña de videojuegos del ABM está conectada a la API: permite listar,
buscar, filtrar, crear, editar y eliminar. Las pestañas futuras de consolas,
desarrolladores y publishers están deshabilitadas hasta sus etapas de
implementación.

## Desarrollo

Desde esta carpeta:

```bash
npm install
npm run dev
```

Para validar el frontend:

```bash
npm run lint
npm run build
```
