# Lucas: matriz de estadísticas para el dashboard

Este documento relaciona las estadísticas de la API con las visualizaciones
actuales del frontend. Las rutas y respuestas se rigen por
[contrato_api_json.md](./contrato_api_json.md); los gráficos están implementados
en `frontend/src/App.jsx`.

## Estadísticas de consolas (hardware)

`GET /api/estadisticas/consolas` devuelve todos estos datos en una sola
respuesta. Los filtros de videojuegos no modifican esta sección.

| Métrica | Dato de `data` | Visualización actual | Unidad |
|---|---|---|---|
| Cantidad de consolas | `summary.consoleCount` | Tarjeta | — |
| Ventas totales de hardware | `summary.totalSales` | Tarjeta | `million_units` |
| Cantidad de fabricantes | `summary.manufacturerCount` | Tarjeta | — |
| Consolas más vendidas | `consoles` (primeras 10) | Barras | `million_units` |
| Ventas por fabricante | `salesByManufacturer` | Barras | `million_units` |
| Ventas por generación | `salesByGeneration` | Barras | `million_units` |
| Consolas lanzadas por década | `releasesByDecade` | Barras de cantidad | consolas |

La tarjeta «Consola más vendida» toma la primera consola de `consoles`, que la
API ordena por ventas descendentes. `releasesByDecade` cuenta lanzamientos de
hardware y no representa ventas de videojuegos por año.

## Estadísticas de videojuegos

Todas estas rutas aceptan los filtros aplicables enviados por el frontend:
`yearFrom`, `yearTo`, `generationId`, `manufacturerId`, `consoleId` y
`publisherId`. Los filtros se combinan con AND; los años son inclusivos.
Cuando no hay filtros, `meta.filters` es `{}`. El frontend aplica los filtros
a todas las consultas de videojuegos y no a las estadísticas de hardware.

| Métrica | Endpoint | Dato principal | Visualización actual |
|---|---|---|---|
| Cantidad de videojuegos | `GET /api/estadisticas/resumen` | `gameCount` | Tarjeta |
| Ventas totales de videojuegos | `GET /api/estadisticas/resumen` | `totalSales` | Tarjeta, `million_copies` |
| Consola líder por ventas de videojuegos | `GET /api/estadisticas/resumen` | `topConsole` | Tarjeta; no son ventas de hardware |
| Generaciones con ventas | `GET /api/estadisticas/ventas-por-generacion` | cantidad de elementos | Tarjeta |
| Videojuegos más vendidos | `GET /api/estadisticas/juegos-mas-vendidos?limit=10` | `title`, `sales` | Barras, top 10 |
| Ventas por publisher | `GET /api/estadisticas/ranking-publishers?limit=10` | `publisherName`, `sales`, `gameCount` | Barras, top 10 |
| Ventas por desarrollador | `GET /api/estadisticas/ranking-desarrolladores?limit=10` | `developerName`, `sales`, `gameCount` | Barras, top 10 |
| Evolución anual de ventas | `GET /api/estadisticas/ventas-por-anio` | `releaseYear`, `sales` | Línea |
| Ventas por consola | `GET /api/estadisticas/ventas-por-consola` | `consoleName`, `sales` | Barras, top 10 en pantalla |
| Ventas por generación | `GET /api/estadisticas/ventas-por-generacion` | `generationNumber`, `sales` | Barras |
| Ventas por fabricante | `GET /api/estadisticas/ventas-por-fabricante` | `manufacturerName`, `sales` | Barras |
| Fabricante dominante por generación | `GET /api/estadisticas/dominador-por-generacion` | generación, fabricante y `sales` | Barras |

Los rankings y juegos más vendidos limitan la respuesta a 10 elementos por
defecto. La pantalla omite de las barras de publishers y desarrolladores los
elementos cuya venta es `null`; la API puede devolverlos para conservar el
`gameCount`. Las ventas conocidas se expresan en millones de copias
(`million_copies`); los valores desconocidos no se suman.

## Validación de rendimiento

No se acordó un objetivo máximo de latencia. El 14 de noviembre de 2026 se
midieron las rutas sin filtros contra la base SQLite local, que contiene 27.206
videojuegos. Se hizo una solicitud de calentamiento y luego cinco solicitudes
por endpoint; se informa mediana y máximo de esos cinco tiempos. Los tiempos
son de ida y vuelta HTTP local en entorno de desarrollo, no un SLA de
producción.

| Endpoint | Mediana (ms) | Máximo (ms) |
|---|---:|---:|
| `/api/estadisticas/consolas` | 3,5 | 7,0 |
| `/api/estadisticas/resumen` | 24,4 | 25,0 |
| `/api/estadisticas/ventas-por-generacion` | 12,2 | 12,7 |
| `/api/estadisticas/ventas-por-consola` | 12,8 | 13,1 |
| `/api/estadisticas/ventas-por-fabricante` | 13,2 | 13,3 |
| `/api/estadisticas/ranking-publishers` | 26,0 | 26,7 |
| `/api/estadisticas/ranking-desarrolladores` | 35,7 | 36,2 |
| `/api/estadisticas/ventas-por-anio` | 16,3 | 17,3 |
| `/api/estadisticas/juegos-mas-vendidos` | 57,4 | 62,1 |
| `/api/estadisticas/dominador-por-generacion` | 14,2 | 14,8 |

Todas las rutas respondieron HTTP 200. En esta medición local no hay evidencia
que justifique agregar caché u optimizaciones; volver a medir si cambia el
tamaño de la base o el entorno.
