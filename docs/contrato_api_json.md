# GameStats: contrato JSON de la API

Este documento define el contrato compartido entre el backend y el frontend.
Enzo, Lucas, Matias e Ivan deben usar estos nombres de campos y formatos para
implementar las APIs, las pantallas y sus datos de prueba. Si se acuerda un
cambio, actualizar este documento y avisar a quienes consumen la API antes de
implementarlo.

## 1. Convenciones generales

- Todas las rutas comienzan con `/api`.
- Las solicitudes y respuestas usan JSON UTF-8.
- Los nombres de propiedades JSON usan `camelCase`, aunque el backend use
  `snake_case` internamente.
- Los IDs son enteros.
- Los valores numéricos se envían como números JSON, no como cadenas.
- Un dato ausente o desconocido se representa como `null`; no se reemplaza por
  `0`, una cadena vacía ni un texto como `"N/A"`.
- Las fechas del catálogo se representan como `releaseYear` (entero de cuatro
  dígitos o `null`), no como fecha completa. Confirmar que el CSV solo tenga el
  año antes de cerrar el esquema. Si el CSV contiene una fecha completa, el
  equipo debe acordar el cambio en este contrato antes de implementarlo.
- `sales` es un número o `null`. Uriel debe confirmar la unidad contra el CSV
  antes de importar. La API y el frontend no convierten unidades; cada respuesta
  estadística incluye la unidad en `meta.unit`.
- Hasta confirmar si el dataset tiene ventas por región, el contrato contempla
  solamente ventas totales (`sales`). Si se necesitan métricas regionales,
  acordar primero el esquema y extender este contrato.

## 2. Formato de respuestas

### Recurso individual

Las respuestas exitosas que devuelven un recurso usan `data`:

```json
{
  "data": {
    "id": 42,
    "title": "Super Mario 64"
  }
}
```

### Colección

Las colecciones usan `data` como arreglo. Las respuestas paginadas agregan
`pagination`:

```json
{
  "data": [],
  "pagination": {
    "page": 1,
    "pageSize": 20,
    "totalItems": 0,
    "totalPages": 0
  }
}
```

Una colección sin resultados devuelve `data: []` y HTTP `200`; no es un error.
Las colecciones no paginadas, como las opciones de un selector, omiten
`pagination`.

### Error

Todos los errores de API usan esta forma:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Hay campos que requieren corrección.",
    "details": [
      {
        "field": "sales",
        "message": "Debe ser un número mayor o igual a cero."
      }
    ]
  }
}
```

`details` puede ser un arreglo vacío cuando no haya errores asociados a campos.
No se deben devolver trazas internas ni detalles sensibles al cliente.

| HTTP | `code` sugerido | Uso |
|---|---|---|
| `400` | `INVALID_REQUEST` | Parámetros o formato de solicitud inválidos |
| `404` | `NOT_FOUND` | No existe el recurso solicitado |
| `409` | `DUPLICATE_RESOURCE` | Ya existe el título en esa consola |
| `422` | `VALIDATION_ERROR` | Campos con valores inválidos |
| `500` | `INTERNAL_ERROR` | Error inesperado del servidor |

## 3. Entidad Videojuego

### Respuesta de un videojuego

Las respuestas de detalle y los elementos del listado usan este formato:

```json
{
  "id": 42,
  "title": "Super Mario 64",
  "console": {
    "id": 12,
    "name": "Nintendo 64"
  },
  "publisher": {
    "id": 3,
    "name": "Nintendo"
  },
  "developer": {
    "id": 8,
    "name": "Nintendo EAD"
  },
  "releaseYear": 1996,
  "sales": 11.91
}
```

- `console` es obligatorio.
- `publisher` y `developer` pueden ser `null`.
- `releaseYear` y `sales` pueden ser `null` cuando el dato se desconozca.
- `sales` conserva la unidad del dataset. Verificarla antes de usarla como
  ventas totales o compararla con otra fuente.

### Crear videojuego

`POST /api/videojuegos` recibe IDs de relaciones, no los objetos anidados:

```json
{
  "title": "Super Mario 64",
  "consoleId": 12,
  "publisherId": 3,
  "developerId": 8,
  "releaseYear": 1996,
  "sales": 11.91
}
```

`title` y `consoleId` son obligatorios. `publisherId`, `developerId`,
`releaseYear` y `sales` son opcionales y aceptan `null`. Si una relación
opcional se informa con un ID, ese ID debe existir.

Una creación exitosa responde HTTP `201` con el videojuego creado dentro de
`data`.

### Actualizar videojuego

`PUT /api/videojuegos/{id}` recibe el objeto editable completo, con la misma
forma que la solicitud de creación. Los campos opcionales que se quieran dejar
vacíos deben enviarse explícitamente como `null`. Responde HTTP `200` con el
recurso actualizado dentro de `data`.

### Eliminar videojuego

`DELETE /api/videojuegos/{id}` responde HTTP `204` sin cuerpo cuando la
eliminación se completa. La implementación debe respetar la decisión del equipo
sobre baja física o lógica.

## 4. Catálogo y selectores

### Listar videojuegos

`GET /api/videojuegos` acepta estos parámetros opcionales:

| Parámetro | Tipo | Descripción |
|---|---|---|
| `page` | entero | Página, empieza en `1`; por defecto `1` |
| `pageSize` | entero | Elementos por página; por defecto `20`, máximo `100` |
| `search` | texto | Busca coincidencias en el título |
| `consoleId` | entero | Filtra por consola |
| `publisherId` | entero | Filtra por publisher |
| `yearFrom` | entero | Año de lanzamiento mínimo, inclusive |
| `yearTo` | entero | Año de lanzamiento máximo, inclusive |

Ejemplo:

```http
GET /api/videojuegos?page=1&pageSize=20&search=mario&consoleId=12&yearFrom=1990&yearTo=2000
```

La respuesta contiene los videojuegos y los metadatos de paginación definidos
arriba. El orden predeterminado es por título ascendente y luego por ID
ascendente, para que la paginación sea estable. `page` menor que `1`,
`pageSize` menor que `1` o mayor que `100`, y `yearFrom` mayor que `yearTo`
devuelven `400 INVALID_REQUEST`.

### Ver detalle

`GET /api/videojuegos/{id}` devuelve HTTP `200` y un videojuego en `data`, o
`404 NOT_FOUND`.

### Opciones para formularios

Las siguientes rutas devuelven HTTP `200` y una colección no paginada:

- `GET /api/consolas`
- `GET /api/publishers`
- `GET /api/desarrolladores`

Formato común:

```json
{
  "data": [
    {
      "id": 12,
      "name": "Nintendo 64"
    }
  ]
}
```

Los elementos se ordenan por `name` ascendente.

## 5. Estadísticas

Todas las rutas estadísticas aceptan los filtros aplicables de esta lista:

| Parámetro | Tipo | Descripción |
|---|---|---|
| `yearFrom` | entero | Año mínimo del videojuego, inclusive |
| `yearTo` | entero | Año máximo del videojuego, inclusive |
| `generationId` | entero | Filtra por generación |
| `manufacturerId` | entero | Filtra por fabricante de la consola |
| `consoleId` | entero | Filtra por consola |
| `publisherId` | entero | Filtra por publisher |

Se omiten los filtros no aplicables a una consulta. Los filtros se combinan con
operación AND. Un parámetro inválido devuelve `400 INVALID_REQUEST`; una
consulta válida sin datos devuelve `200` con `data: []`.

`GET /api/estadisticas/juegos-mas-vendidos` también acepta `limit` (entero,
por defecto `10`, mínimo `1`, máximo `100`) para indicar cuántos resultados
devolver. Un valor fuera de ese rango devuelve `400 INVALID_REQUEST`.

Cada respuesta estadística usa el mismo envoltorio:

```json
{
  "data": [],
  "meta": {
    "unit": "million_copies",
    "filters": {
      "yearFrom": 2000,
      "yearTo": 2010
    }
  }
}
```

`meta.unit` indica la unidad de los valores de ventas y debe coincidir con la
unidad real confirmada del dataset. En el resumen, `gameCount` siempre cuenta
juegos y `meta.unit` aplica a `totalSales` y a las ventas de `topConsole`.
`meta.filters` incluye los filtros efectivamente aplicados y vale `{}` si no se
aplicó ninguno.

### Rutas y forma de cada elemento

| Ruta | Elemento de `data` |
|---|---|
| `GET /api/estadisticas/resumen` | Un objeto con `gameCount`, `totalSales` y `topConsole` (`{ "id", "name", "sales" }` o `null`) |
| `GET /api/estadisticas/ventas-por-generacion` | `{ "generationId", "generationNumber", "sales" }` |
| `GET /api/estadisticas/ventas-por-consola` | `{ "consoleId", "consoleName", "sales" }` |
| `GET /api/estadisticas/ventas-por-fabricante` | `{ "manufacturerId", "manufacturerName", "sales" }` |
| `GET /api/estadisticas/ranking-publishers` | `{ "publisherId", "publisherName", "sales", "gameCount" }` |
| `GET /api/estadisticas/ranking-desarrolladores` | `{ "developerId", "developerName", "sales", "gameCount" }` |
| `GET /api/estadisticas/ventas-por-anio` | `{ "releaseYear", "sales" }` |
| `GET /api/estadisticas/juegos-mas-vendidos` | `{ "gameId", "title", "consoleName", "releaseYear", "sales" }` |
| `GET /api/estadisticas/dominador-por-generacion` | `{ "generationId", "generationNumber", "manufacturer": { "id", "name" }, "sales" }` |

El resumen devuelve `data` como objeto; las demás rutas devuelven `data` como
arreglo. Para empates en rankings, ordenar por nombre ascendente como criterio
secundario. Los registros sin la dimensión requerida (por ejemplo, publisher
desconocido en el ranking de publishers) se excluyen de ese ranking. Los
valores desconocidos de ventas no se suman.

Ejemplo de ranking:

```json
{
  "data": [
    {
      "publisherId": 3,
      "publisherName": "Nintendo",
      "sales": 125.4,
      "gameCount": 38
    }
  ],
  "meta": {
    "unit": "million_copies",
    "filters": {}
  }
}
```

## 6. Acuerdos pendientes de validar con los datos

Antes de importar la base y cerrar la implementación:

1. **Uriel** confirma si `releaseYear` representa correctamente la columna de
   lanzamiento y si hay datos regionales además de ventas totales.
2. **Uriel** documenta la unidad real de ventas. Si no son millones de copias,
   actualizar los ejemplos de `meta.unit` y comunicarlo a Lucas y Matias.
3. **Uriel, Enzo y Lucas** confirman que los filtros, campos opcionales y
   relaciones coinciden con el dataset y el esquema final.
4. **Enzo y Lucas** publican todos los errores y respuestas en OpenAPI usando
   este contrato.
5. **Matias e Ivan** mantienen sus datos de prueba con las mismas propiedades y
   tipos definidos aquí, y los reemplazan por llamadas reales durante la
   integración.
