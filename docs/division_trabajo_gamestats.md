# GameStats: plan de trabajo para 5 desarrolladores

## Reparto de responsabilidades

Cada punto tiene una persona responsable. El responsable organiza el trabajo de
su parte, mantiene sus archivos y comunica a tiempo bloqueos o cambios de
contrato. Los nombres se pueden reemplazar por los del equipo.

| Responsable | Rol | Punto |
|---|---|---|
| Uriel | Base de datos | Esquema, dataset e importación |
| Enzo | Backend | API del catálogo (ABM) |
| Lucas | Backend | API de estadísticas |
| Matias | Frontend | Dashboards |
| Ivan | Frontend | Estructura general y ABM |

Uriel es responsable del esquema y la carga de datos, pero debe acordar el
modelo con Enzo y Lucas antes de fijarlo. Matias e Ivan acuerdan entre sí la
navegación y los componentes compartidos. Cada desarrollador prueba su parte y
participa en la integración final.

## Orden de trabajo

### Etapa 1: acuerdos del equipo

Antes de desarrollar funcionalidades en paralelo:

1. **Uriel** revisa el CSV y comparte sus columnas, ejemplos, tipos de datos y
   cantidad de registros.
2. **Uriel, Enzo y Lucas** validan las entidades y sus relaciones:
   `Fabricante`, `Generacion`, `Consola`, `Publisher`, `Desarrollador` y
   `Videojuego`.
3. El equipo decide y documenta:
   - Si las ventas disponibles son totales o están separadas por región.
   - Si el dataset trae una fecha completa o solamente el año de lanzamiento.
   - Qué campos pueden faltar, especialmente publisher y desarrollador.
   - Si al borrar un videojuego se hace una baja física o lógica.
   - Qué unidad representan las ventas y cómo se muestran los valores faltantes.
4. **Enzo y Lucas** revisan con **Matias e Ivan** el contrato JSON compartido en
   [contrato_api_json.md](./contrato_api_json.md). Ese documento define
   propiedades, tipos, respuestas, errores, filtros y ejemplos para que las
   APIs y los datos de prueba del frontend se implementen de forma compatible.
5. **Uriel** confirma en el CSV las decisiones pendientes sobre año de
   lanzamiento y unidad/disponibilidad de ventas; el equipo actualiza el
   contrato si hace falta antes de conectar los datos reales.

**Salida de la etapa:** esquema acordado, decisiones registradas y contratos
de API disponibles para todo el equipo. El contrato de referencia es
[contrato_api_json.md](./contrato_api_json.md).

### Etapa 2: desarrollo en paralelo (puntos 1 a 5)

Una vez cerrados los acuerdos de la Etapa 1, los cinco puntos se pueden
desarrollar en paralelo. No hace falta esperar a que la base o las APIs estén
terminadas para empezar las interfaces:

- **Punto 1 — Uriel:** prepara la base y la importación.
- **Punto 2 — Enzo:** desarrolla el ABM usando el esquema y el contrato
  acordados.
- **Punto 3 — Lucas:** desarrolla las consultas de estadísticas usando el mismo
  esquema y el contrato acordado.
- **Punto 4 — Matias:** desarrolla los dashboards con datos de prueba.
- **Punto 5 — Ivan:** desarrolla navegación y catálogo; puede usar datos de
  prueba para las operaciones del ABM.

Mientras Enzo y Lucas implementan y prueban sus APIs, Matias e Ivan deben usar
datos de prueba locales que respeten exactamente los formatos JSON, campos,
filtros y respuestas de error definidos en
[contrato_api_json.md](./contrato_api_json.md). Los datos de prueba son
temporales: sirven para construir y validar las pantallas, no reemplazan la
integración con la API real. Así, las interfaces pueden avanzar en paralelo sin
esperar a los endpoints.

### Etapa 3: integración final y pruebas conjuntas

Cuando la base y ambas APIs estén disponibles, se dejan de usar los datos de
prueba para los flujos integrados y se conectan las interfaces a los endpoints
reales:

1. **Uriel** entrega la base reproducible, limpia y poblada, junto con los pasos
   para crearla y cargarla.
2. **Enzo y Lucas** verifican sus endpoints contra esa base y confirman que
   respetan los contratos documentados.
3. **Matias** reemplaza los datos de prueba de los dashboards por llamadas a la
   API de estadísticas de Lucas.
4. **Ivan** reemplaza los datos de prueba del catálogo por llamadas a la API del
   ABM de Enzo.
5. **Matias e Ivan** comprueban carga, resultados vacíos, errores, filtros y
   mensajes de la interfaz con respuestas reales.
6. **Los cinco desarrolladores** recorren juntos los flujos principales desde
   el frontend hasta la base: consultas del catálogo, alta, edición y baja de
   videojuegos, y carga de dashboards con filtros.
7. El equipo corrige errores de integración, repite las pruebas y actualiza las
   instrucciones de ejecución antes de dar el proyecto por terminado.

---

## Punto 1 — Uriel: base de datos e importación

**Objetivo:** entregar una base SQLite reproducible, con el esquema acordado y
los datos preparados para el catálogo y las estadísticas.

### Tareas

1. **Inspeccionar el dataset**
   - Registrar nombre y origen del archivo, columnas, tipos, cantidad de filas
     y ejemplos representativos.
   - Identificar nulos, duplicados, valores fuera de rango y nombres escritos
     de formas diferentes.
   - Confirmar cómo se representan año/fecha, ventas y valores desconocidos.
   - Compartir los hallazgos con Enzo y Lucas antes de fijar el esquema.
2. **Definir y documentar el modelo relacional**
   - Crear las tablas de fabricantes, generaciones, consolas, publishers,
     desarrolladores y videojuegos, con claves primarias y foráneas.
   - Definir qué campos son obligatorios y cuáles aceptan nulos según los datos
     reales.
   - Respetar la regla acordada para el mismo título en una misma consola.
   - Evitar guardar fabricante o generación duplicados en videojuegos: se
     obtienen mediante la consola.
   - Acordar cómo se almacenan las ventas regionales, si el dataset las trae.
3. **Preparar la base y el esquema**
   - Implementar el esquema de acuerdo con la decisión del equipo y los modelos
     ORM existentes, evitando mantener dos definiciones incompatibles.
   - Incluir restricciones e índices útiles para claves foráneas, título,
     consola y año, justificando los índices.
   - Permitir que otra persona cree la base desde cero siguiendo instrucciones
     documentadas.
4. **Limpiar e importar**
   - Normalizar espacios, nombres y formatos; documentar las reglas de limpieza.
   - Resolver duplicados según la regla acordada y registrar los descartes o
     correcciones relevantes.
   - Importar primero las entidades de referencia y después consolas y juegos,
     conservando correctamente sus relaciones.
   - Hacer que la carga se pueda repetir sin crear duplicados ni requerir pasos
     manuales ocultos.
5. **Verificar y entregar**
   - Comparar filas de entrada, importadas, descartadas y con datos faltantes.
   - Ejecutar consultas de control: claves foráneas válidas, conteos por tabla
     y algunos registros revisados manualmente.
   - Crear un diccionario de datos con significado, tipo, obligatoriedad,
     unidad y origen de cada campo.

### Entregables y criterio de terminado

- Esquema/modelo documentado y alineado con el backend.
- Script o procedimiento reproducible para crear y cargar SQLite.
- Base de datos poblada o instrucciones claras para generarla.
- Reglas de limpieza, resumen de importación y diccionario de datos.
- La carga termina sin errores y las verificaciones de integridad pasan.

**Coordina con:** Enzo y Lucas para el esquema; todo el equipo para las
decisiones del dataset.

---

## Punto 2 — Enzo: backend del ABM

**Objetivo:** exponer operaciones para listar y mantener videojuegos, junto con
los datos auxiliares que necesitan los formularios.

Usar [contrato_api_json.md](./contrato_api_json.md) como referencia para nombres
de campos, tipos, solicitudes, respuestas y errores.

### Tareas

1. **Preparar el acceso a datos**
   - Usar la configuración de base de datos y las entidades acordadas con
     Uriel.
   - Verificar relaciones entre videojuegos, consolas, publishers y
     desarrolladores.
   - Mantener separadas las responsabilidades de rutas, validación, lógica y
     consultas según la estructura del backend.
2. **Implementar los endpoints del catálogo**
   - Listar videojuegos con paginación.
   - Buscar por título y permitir filtros acordados (por ejemplo consola,
     publisher o año).
   - Obtener el detalle de un videojuego por ID.
   - Crear, modificar y eliminar un videojuego.
   - Implementar endpoints de consulta para llenar los selectores de consolas,
     publishers y desarrolladores.
3. **Validar entradas y errores**
   - Validar campos obligatorios, longitudes, fechas/años y ventas numéricas no
     negativas.
   - Aceptar publisher y desarrollador ausentes si el esquema los permite.
   - Comprobar que los IDs relacionados existan.
   - Detectar título duplicado en la misma consola.
   - Responder con códigos HTTP y mensajes consistentes: recurso inexistente,
     entrada inválida, duplicado y error inesperado.
   - Aplicar la decisión del equipo sobre baja física o lógica en todas las
     operaciones relacionadas.
4. **Documentar y probar**
   - Documentar rutas, parámetros, cuerpos de solicitud y ejemplos de
     respuesta en OpenAPI/Swagger.
   - Probar casos exitosos y errores: creación válida, ID inexistente, campos
     inválidos, relaciones inexistentes y duplicado.
   - Probar paginación, búsqueda y filtros combinados.

### Rutas sugeridas

El equipo puede ajustarlas, pero debe acordar una sola convención con el
frontend. Por ejemplo:

- `GET /api/videojuegos`
- `GET /api/videojuegos/{id}`
- `POST /api/videojuegos`
- `PUT /api/videojuegos/{id}`
- `DELETE /api/videojuegos/{id}`
- `GET /api/consolas`
- `GET /api/publishers`
- `GET /api/desarrolladores`

### Entregables y criterio de terminado

- ABM accesible desde la API y conectado a la base acordada.
- Validaciones y respuestas de error coherentes.
- Documentación visible en Swagger/OpenAPI y pruebas de los casos principales.
- Ivan puede realizar el flujo de alta, consulta, edición y baja usando el
  contrato documentado.

**Coordina con:** Uriel para el esquema e Ivan para el contrato y el flujo de
pantallas.

---

## Punto 3 — Lucas: backend de estadísticas

**Objetivo:** proveer datos agregados confiables y preparados para los gráficos
del dashboard.

Usar [contrato_api_json.md](./contrato_api_json.md) como referencia para rutas,
filtros, estructura de las respuestas y metadatos de unidad.

### Tareas

1. **Definir las métricas**
   - Confirmar con Uriel el significado, unidad y disponibilidad de las ventas.
   - Definir cómo se tratan los nulos y qué significa cada indicador.
   - Acordar con Matias qué gráfico consume cada estadística y qué filtros usa.
2. **Implementar consultas**
   - Ventas por generación.
   - Unidades/ventas por consola y por fabricante.
   - Ranking de publishers y desarrolladores.
   - Evolución de ventas por año.
   - Videojuegos más vendidos.
   - Fabricante con más ventas por generación, usando la relación videojuego →
     consola → generación/fabricante.
   - Indicadores generales que el equipo acuerde, como cantidad de juegos,
     ventas totales y consola más vendida.
3. **Agregar filtros**
   - Permitir filtros acordados, como intervalo de años, generación,
     fabricante, consola o publisher.
   - Validar parámetros inválidos y documentar el comportamiento ante filtros
     sin resultados.
   - Asegurar que todas las estadísticas relevantes apliquen los filtros de
     forma consistente.
4. **Diseñar respuestas útiles para gráficos**
   - Mantener una forma JSON consistente y documentada.
   - Incluir etiquetas, valores y unidades; definir cómo se representan
     valores faltantes.
   - Evitar que el frontend tenga que recalcular agregaciones que corresponden
     al backend.
5. **Medir, probar y documentar**
   - Comparar resultados de consultas con cálculos de control sobre una muestra.
   - Probar filtros, rangos vacíos, nulos y empates en rankings.
   - Medir las consultas sobre la base completa; agregar optimizaciones sólo
     si hacen falta.
   - Documentar endpoint, parámetros, respuesta y gráfico asociado.

### Entregables y criterio de terminado

- Endpoints de estadísticas documentados y conectados a la base acordada.
- Tabla de correspondencia entre estadística, endpoint, filtros y gráfico.
- Pruebas que validan agregaciones y filtros con datos conocidos.
- Matias puede reemplazar los datos de ejemplo por respuestas reales.

**Coordina con:** Uriel por el significado y calidad de los datos; Matias por
respuestas, filtros y gráficos.

---

## Punto 4 — Matias: frontend de dashboards

**Objetivo:** construir dashboards claros, responsivos e interactivos usando
las estadísticas de la API.

Los datos de prueba y las llamadas a la API deben respetar
[contrato_api_json.md](./contrato_api_json.md).

### Tareas
1. **Acordar vistas y métricas**
   - Revisar con Lucas las métricas y los formatos de respuesta.
   - Definir con Ivan navegación, nombres de secciones y componentes visuales
     compartidos.
   - Priorizar una vista general y vistas para consolas/generaciones,
     empresas y juegos más vendidos.
2. **Construir las pantallas**
   - Crear tarjetas para los indicadores principales.
   - Elegir gráficos apropiados para comparar categorías y observar tendencias.
   - Incluir la visualización de fabricante dominante por generación.
   - Mostrar títulos, leyendas, unidades y formatos numéricos entendibles.
3. **Conectar datos**
   - Mientras Lucas termina la API, usar datos de ejemplo con el contrato
     acordado.
   - Centralizar las llamadas a la API y reemplazar los ejemplos sin cambiar
     innecesariamente la forma de las pantallas.
   - Conectar filtros y actualizar gráficos al cambiar sus valores.
4. **Resolver estados y accesibilidad**
   - Mostrar estado de carga, error y resultado vacío.
   - Evitar gráficos rotos o confusos ante valores nulos o una sola categoría.
   - Revisar diseño en móvil y escritorio, contraste, etiquetas y navegación
     con teclado.
5. **Probar**
   - Verificar que cada gráfico represente los datos y filtros recibidos.
   - Probar fallos de red, respuestas vacías y cambios repetidos de filtros.
   - Confirmar que las páginas se integren con las rutas y el layout de Ivan.

### Entregables y criterio de terminado

- Dashboards integrados a la aplicación y conectados a estadísticas reales.
- Componentes adaptables con estados de carga, error y vacío.
- Métricas y filtros consistentes con la documentación de la API.

**Coordina con:** Lucas por la API e Ivan por rutas, layout y estilos comunes.

---

## Punto 5 — Ivan: frontend del ABM y estructura general

**Objetivo:** proporcionar navegación y una sección de catálogo desde la que el
usuario pueda mantener videojuegos.

Los datos de prueba y las llamadas a la API deben respetar
[contrato_api_json.md](./contrato_api_json.md).

### Tareas

1. **Crear la estructura de la aplicación**
   - Definir layout, menú, rutas principales y página inicial.
   - Crear los espacios/rutas para Catálogo y Dashboards.
   - Acordar con Matias estilos, componentes comunes y navegación.
2. **Implementar el listado**
   - Mostrar videojuegos en una tabla o lista con paginación.
   - Agregar búsqueda por título y filtros acordados con Enzo.
   - Mostrar los datos relevantes y acciones de ver, editar y eliminar.
   - Resolver carga, error y lista vacía.
3. **Implementar formularios**
   - Crear formularios de alta y edición.
   - Cargar consolas, publishers y desarrolladores desde los endpoints
     auxiliares.
   - Validar campos requeridos, ventas y fechas/años según el contrato.
   - Respetar campos opcionales, mostrar errores de API y conservar los valores
     ingresados cuando una operación falla.
4. **Conectar las operaciones**
   - Usar una capa común para llamadas HTTP, compartible con Matias.
   - Conectar listado, detalle, alta, edición y eliminación con la API de Enzo.
   - Confirmar antes de eliminar y reflejar la baja según la decisión del
     equipo.
   - Mostrar confirmaciones de éxito y errores comprensibles.
5. **Probar el flujo completo**
   - Probar búsqueda, filtros, paginación y formularios.
   - Probar duplicados, campos inválidos, IDs relacionados inexistentes y
     errores de red.
   - Revisar diseño adaptable y consistencia visual con los dashboards.

### Entregables y criterio de terminado

- Aplicación navegable con rutas de catálogo y dashboards.
- ABM conectado al backend y con validación y mensajes de error.
- Enzo puede verificar que el frontend usa correctamente el contrato de la
  API.

**Coordina con:** Enzo por el ABM y Matias por el layout, navegación y módulos
compartidos.

---

## Tareas compartidas por los cinco desarrolladores

- **Contrato y cambios:** avisar al equipo antes de cambiar campos, rutas,
  nombres o formatos; actualizar documentación y consumidores afectados.
- **Git:** trabajar en ramas descriptivas, integrar cambios mediante revisión y
  no subir archivos de entorno local, credenciales ni bases temporales.
- **Integración:** probar conjuntamente frontend, API y SQLite con instrucciones
  reproducibles antes de la entrega.
- **Calidad:** cada responsable prueba su parte y deja instrucciones para
  reproducir las verificaciones.
- **Documentación:** mantener el README actualizado con requisitos, instalación,
  ejecución y ubicación de la documentación de API.
- **Presentación:** cada desarrollador explica objetivo, decisiones,
  implementación, pruebas y dificultades de su punto.

## Lista de verificación para la entrega

- [ ] Una persona nueva puede preparar el entorno siguiendo el README.
- [ ] La base se puede crear y cargar siguiendo pasos documentados.
- [ ] El catálogo permite listar, buscar, crear, editar y eliminar videojuegos.
- [ ] Los dashboards muestran estadísticas obtenidas desde la API.
- [ ] Las validaciones y errores se entienden desde la interfaz.
- [ ] Los filtros del frontend llegan al backend y modifican los resultados.
- [ ] Se probaron datos vacíos, faltantes y errores de conexión.
- [ ] No hay discrepancias conocidas entre entidades, contratos y documentación.
