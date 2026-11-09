# GameStats: división del trabajo en 5 partes

Cada parte incluye qué hace, tareas concretas y qué entrega.

## 1. Base de datos e importación

**Responsabilidad:** que los datos estén limpios, ordenados y en una base que el resto del equipo pueda usar. Es la base de todo, así que tiene que tener el esquema listo en los primeros días.

- Diseñar el modelo relacional. Tablas posibles: `fabricante`, `generacion`, `consola`, `publisher`, `desarrollador` y `videojuego`, con sus claves foráneas. Si el dataset trae ventas por región, definir si van como columnas o en una tabla aparte.
- Limpiar el CSV de Kaggle: nulos, duplicados, fechas con formatos distintos y nombres inconsistentes (la misma empresa escrita de dos maneras).
- Escribir el script de importación (por ejemplo en Python con pandas) que cargue todo a la base.
- Crear índices en las columnas que se van a consultar mucho (consola, publisher, año).

**Entrega:** diagrama entidad-relación, script SQL del esquema, script de carga, base poblada y un diccionario de datos que explique cada tabla y columna.

## 2. Backend del ABM

**Responsabilidad:** la API que permite mantener el catálogo de videojuegos.

- Endpoints CRUD: listar (con paginación, filtros y búsqueda por título), ver uno, crear, modificar y eliminar.
- Endpoints auxiliares que devuelvan consolas, publishers y desarrolladores, para llenar los desplegables de los formularios.
- Validaciones: campos obligatorios, ventas numéricas y no negativas, fechas válidas, existencia de la consola/publisher referenciados y control de duplicados (mismo título en la misma consola).
- Decidir qué pasa al borrar (baja física o lógica) y devolver códigos HTTP y mensajes de error claros.

**Entrega:** API funcionando, documentada (Swagger/OpenAPI o un README con las rutas) y con pruebas de los casos principales.

## 3. Backend de estadísticas

**Responsabilidad:** las consultas que alimentan los dashboards, replicando lo que hicieron en Power BI.

- Endpoints agregados, por ejemplo: ventas por generación, unidades por consola, unidades por fabricante, ranking de publishers y desarrolladores, evolución de ventas por año y juegos más vendidos.
- El más interesante: "qué empresa dominó cada época", o sea el fabricante con más ventas en cada generación.
- Soporte de filtros (rango de años, generación, fabricante) para que el frontend pueda hacer los gráficos interactivos.
- Devolver los datos en JSON con un formato cómodo para graficar (listas de etiquetas y valores).
- Optimizar las consultas pesadas (JOINs y GROUP BY sobre 27 mil registros) y, si hace falta, cachear resultados.

**Entrega:** endpoints documentados y una tabla que indique qué consulta corresponde a qué gráfico.

## 4. Frontend de dashboards

**Responsabilidad:** que los gráficos se vean bien y se puedan explorar.
- Páginas organizadas por tema, por ejemplo: panorama general, consolas y generaciones, empresas, juegos más vendidos y "quién dominó cada época".
- Tarjetas con indicadores clave (total de juegos, ventas totales, consola más vendida).
- Gráficos de barras, líneas, tortas o similares, con una librería como Chart.js, Plotly o Recharts.
- Filtros interactivos conectados a los parámetros de la API.
- Estados de carga y de error, y diseño adaptable a distintos tamaños de pantalla.

**Entrega:** las vistas de dashboards funcionando contra la API real. Mientras el backend no esté listo, puede trabajar con datos de ejemplo.

## 5. Frontend del ABM y estructura general

**Responsabilidad:** el esqueleto de la aplicación y toda la parte de gestión.

- Layout general: menú de navegación, rutas entre secciones y página de inicio.
- Listado del catálogo con tabla paginada, buscador y filtros.
- Formularios de alta y edición con validación del lado del cliente (antes de llamar a la API).
- Confirmación antes de eliminar y mensajes de éxito o error.
- Estilos compartidos (colores, botones, tipografías) y un módulo común para llamar a la API, que también va a usar la persona 4.

**Entrega:** la sección "Catálogo" completa y la estructura general donde se enchufan los dashboards.

## Tareas compartidas

Hay trabajo que conviene repartir entre todos para que nadie quede cargado:

- **Integración:** probar que todo funcione junto antes de la entrega.
- **Documentación:** README con instrucciones para instalar y correr el proyecto.
- **Informe y presentación:** cada uno explica su parte.

## Orden sugerido

1. Primero: la persona 1 define el esquema, y entre todos acuerdan el contrato de la API (rutas y formato de respuestas).
2. Después: las personas 2 y 3 desarrollan los endpoints, y las 4 y 5 arman las pantallas con datos de ejemplo.
3. Al final: conectan frontend con backend, prueban y pulen.
