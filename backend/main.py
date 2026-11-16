from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from errors import register_exception_handlers
from routers import auth, catalogo, estadisticas, videojuegos

app = FastAPI(title="GameStats API")

register_exception_handlers(app)
app.include_router(auth.router)
app.include_router(catalogo.router)
app.include_router(estadisticas.router)
app.include_router(videojuegos.router)


def _openapi_schema() -> dict[str, Any]:
    if app.openapi_schema is not None:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        routes=app.routes,
    )
    for path, path_item in schema["paths"].items():
        if path.startswith("/api/estadisticas/"):
            for operation in path_item.values():
                if isinstance(operation, dict) and "responses" in operation:
                    # These query errors are normalized to HTTP 400 by errors.py.
                    operation["responses"].pop("422", None)

    app.openapi_schema = schema
    return schema


app.openapi = _openapi_schema