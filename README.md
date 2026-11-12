# GameStats

Plataforma de análisis y gestión de consolas y videojuegos. Aplicación web que integra dashboards con datos históricos de ventas de videojuegos y consolas, y un módulo de gestión (ABM) para mantener el catálogo.

## Tecnologías

| Capa | Tecnología |
|---|---|
| Backend | Python con FastAPI y SQLAlchemy |
| Frontend | React (Vite) sobre Node.js |
| Base de datos | SQLite |

## Requisitos previos

- **Git**
- **Python 3.10 o posterior**
- **Node.js LTS** y npm

Opcionales pero recomendadas:

- **Visual Studio Code** con las extensiones Python y ES7+ React/Redux/React-Native snippets.
- **Postman** o la extensión *REST Client* de VS Code para probar los endpoints de la API.

## Puesta en marcha

### 1. Clonar el repositorio

```bash
git clone <URL-DEL-REPOSITORIO>
cd <NOMBRE-DEL-REPOSITORIO>
```

### 2. Levantar el backend

Desde la raíz del repositorio:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

La API estará disponible en `http://127.0.0.1:8000`. FastAPI ofrece su documentación interactiva en `http://127.0.0.1:8000/docs`.

### 3. Levantar el frontend

En una segunda terminal, desde la raíz del repositorio:

```bash
cd frontend
npm install
npm run dev
```

El frontend queda disponible en `http://localhost:5173`.

Backend y frontend se ejecutan al mismo tiempo, cada uno en su propia terminal.

### 4. Conexión entre frontend y backend

En desarrollo, Vite redirige las llamadas que empiezan con `/api` hacia `http://127.0.0.1:8000`. Las rutas de la API que use el frontend deben comenzar con `/api`.

### 5. Crear y poblar la base SQLite

Desde la raíz del repositorio, ejecutar:

```powershell
cd backend
python -m pip install -r requirements.txt
python -m data.import_consoles
```

El importador crea `backend/data/gamestats.db` y las tablas declaradas por los
modelos SQLAlchemy. Lee `backend/data/docs/Console_Data.csv` y relaciona
fabricantes, generaciones y consolas. Se puede volver a ejecutar: actualiza las
consolas que ya existen y agrega las nuevas, sin borrar datos.

Los años de lanzamiento y discontinuación se guardan como años, no como fechas
inventadas. Los rangos de generación abiertos (`año-Ongoing`) guardan el año de
fin como desconocido. El valor `ongoing` en discontinuación se representa con
`sigue_en_produccion`; las ventas se conservan en la unidad de origen del CSV:
millones de unidades. Como el dataset no incluye países, el importador completa
ese dato con el mapeo de países de origen proporcionado para Atari, Magnavox,
Mattel, Microsoft, Nintendo, Sega y Sony. El archivo `.db` es generado
localmente y está excluido de Git.

### 6. Consultar una consola por ID

Después de preparar la base, ejecutar desde `backend`:

```powershell
python -m data.query_console
```

Ingresar el ID de la consola. El programa muestra sus datos y, de forma
escalonada, el fabricante, la generación y los videojuegos asociados, incluyendo
publisher y desarrollador cuando están disponibles.

## Estructura del proyecto

```text
.
├── backend/
│   ├── data/             Acceso a datos y configuración de persistencia
│   ├── models/           Modelos del dominio
│   ├── repositories/     Consultas y operaciones de persistencia
│   ├── routers/          Definición y agrupación de rutas de la API
│   ├── schemas/          Esquemas de entrada y salida de la API
│   ├── services/         Lógica de negocio
│   ├── main.py           Aplicación FastAPI
│   └── requirements.txt  Dependencias de Python
├── frontend/
│   └── src/
│       ├── api/          Módulo común para llamar a la API
│       ├── components/   Componentes reutilizables
│       └── pages/        Pantallas (dashboards, catálogo)
├── data/                 Dataset original (si corresponde)
└── docs/                 Diagrama ER, diccionario de datos, contrato de la API
```

## Flujo de trabajo con Git

- La rama `main` debe estar siempre en un estado que compile y funcione.
- Cada integrante trabaja en su propia rama, por ejemplo `feature/abm-backend` o `feature/dashboards-frontend`.
- Hacer `git pull` antes de empezar a trabajar y antes de subir cambios.
- Los cambios llegan a `main` mediante Pull Request, revisado por al menos otra persona.

## Problemas frecuentes

**PowerShell no permite activar el entorno virtual.**
Es la política de ejecución de Windows. Se puede activar el entorno desde cmd con `.venv\Scripts\activate.bat` o ajustar la política de usuario con:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

**No se encuentra `uvicorn` o `fastapi`.**
Verificar que el entorno virtual esté activado y correr `python -m pip install -r requirements.txt` desde `backend`.

**El frontend no logra comunicarse con la API.**
Verificar que el backend esté corriendo en el puerto `8000` y que las llamadas del frontend usen el prefijo `/api`.

## Integrantes

### Backend
- Uriel Maceri (DBA)
- Enzo Paez
- Lucas Roman 

### Frontend
- Matias Mamani
- Ivan Bonanata

## Ejecución rápida (Windows)

En la raíz del repositorio hay dos scripts para simplificar el trabajo diario:

| Script | Qué hace |
|---|---|
| `build.bat` | Prepara el entorno Python y crea/actualiza la base SQLite desde el CSV, sin borrarla |
| `run.bat` | Levanta el backend y el frontend, cada uno en su propia ventana |

```bat
build.bat
run.bat
```

- `run.bat` crea el entorno virtual e instala las dependencias del backend si todavía no están instaladas; también instala las dependencias del frontend la primera vez.
- `build.bat` crea las tablas que falten e importa o actualiza las consolas del CSV. No borra la base ni los videojuegos existentes.
- `build.bat nopause` omite la pausa final.
- Para detener los servicios, cerrar cada ventana o presionar `Ctrl+C` en ellas.
