# GameStats

Plataforma de análisis y gestión de consolas y videojuegos. Aplicación web que integra dashboards con datos históricos de ventas de videojuegos y consolas, y un módulo de gestión (ABM) para mantener el catálogo.

## Tecnologías

| Capa | Tecnología |
|---|---|
| Backend | Python con FastAPI y SQLAlchemy |
| Frontend | React (Vite) sobre Node.js |
| Base de datos | SQLite |

## Descripción

GameStats permite explorar estadísticas de consolas y videojuegos, y administrar el catálogo de videojuegos desde una aplicación web. El backend expone una API REST que consulta una base SQLite; el frontend consume esa API para presentar gráficos, filtros y operaciones del catálogo.

La sección de estadísticas incluye métricas de consolas —ventas por fabricante y generación, y lanzamientos por década— y estadísticas de videojuegos como ventas por año, consola, generación y fabricante, rankings de publishers y desarrolladores, juegos más vendidos y filtros por período, consola, generación, fabricante o publisher.

El ABM permite listar, buscar, filtrar, crear, editar y eliminar videojuegos. Los selectores de consola, publisher y desarrollador se obtienen del catálogo disponible en la API.

## Requisitos

- Python 3.10 o posterior
- Node.js LTS y npm
- Git, para clonar el repositorio

## Inicio rápido en Windows

Desde la raíz del repositorio, ejecutar:

```bat
BUILD.bat
RUN.bat
```

`BUILD.bat` prepara el entorno virtual del backend si hace falta y crea o actualiza la base de datos importando los CSV de consolas y videojuegos. No borra los datos existentes. `RUN.bat` inicia el backend y el frontend en ventanas separadas; la primera vez instala las dependencias necesarias.

Al iniciar los servicios:

- Aplicación web: <http://localhost:5173>
- API y documentación interactiva: <http://127.0.0.1:8000/docs>

Para detenerlos, cerrar las ventanas correspondientes o presionar `Ctrl+C` en cada una.

## Instalación y ejecución manual

### Backend

Desde la raíz del repositorio, crear y activar un entorno virtual e instalar las dependencias:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Crear o actualizar la base SQLite a partir de los datos incluidos:

```powershell
python -m data.import_consoles
python -m data.import_games
```

Iniciar la API:

```powershell
python -m uvicorn main:app --reload
```

La API estará disponible en `http://127.0.0.1:8000`. La interfaz interactiva de FastAPI está en `/docs`.

### Frontend

En una segunda terminal, desde la raíz del repositorio:

```powershell
cd frontend
npm install
npm run dev
```

La aplicación estará disponible en `http://localhost:5173`. Durante el desarrollo, Vite reenvía las solicitudes `/api` al backend en `http://127.0.0.1:8000`.

## Datos

Los importadores utilizan `backend/data/docs/Console_Data.csv` y `backend/data/docs/scrapped_data.csv`, y guardan la base local en `backend/data/gamestats.db`. La base se genera localmente y no se versiona en Git.

Las ventas de consolas se expresan en millones de unidades y las ventas de videojuegos en millones de copias, según sus datasets. Los valores ausentes se conservan como desconocidos; para más detalles sobre importación y formatos, consultar la documentación de la API.

## API

Todas las rutas comienzan con `/api`. Entre las principales secciones se encuentran:

- `/api/estadisticas/...`: resúmenes, agregaciones y rankings de consolas y videojuegos.
- `/api/videojuegos`: listado paginado, detalle y operaciones de creación, edición y eliminación.
- `/api/consolas`, `/api/publishers` y `/api/desarrolladores`: opciones para el catálogo y los formularios.

La especificación OpenAPI está disponible en `/docs` con el backend en ejecución. El contrato y los documentos funcionales se encuentran en [`docs/`](docs/), especialmente [`contrato_api_json.md`](docs/contrato_api_json.md) y [`matriz_estadisticas_dashboard.md`](docs/matriz_estadisticas_dashboard.md).

## Pruebas y validaciones

Desde `backend`, ejecutar las pruebas:

```powershell
python -m pytest
```

Desde `frontend`, validar el código y generar la compilación de producción:

```powershell
npm run lint
npm run build
```

## Estructura del repositorio

```text
backend/
  data/          Conexión a SQLite e importadores de datos
  models/        Modelos de dominio y persistencia
  repositories/  Consultas y acceso a datos
  routers/       Rutas de la API
  schemas/       Esquemas de entrada y salida
  services/      Lógica de negocio
  tests/         Pruebas del backend
frontend/
  src/api/       Clientes para los endpoints
  src/components/ Componentes de estadísticas y gestión
  src/pages/     Pantallas de la aplicación
docs/            Contrato de API y documentación del proyecto
```

## Integrantes

### Backend
- Uriel Maceri (DBA)
- Enzo Paez
- Lucas Roman

### Frontend
- Matias Mamani
- Ivan Bonanata
