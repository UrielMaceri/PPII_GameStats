from fastapi import FastAPI

from errors import register_exception_handlers
from routers import catalogo, estadisticas, videojuegos

app = FastAPI(title="GameStats API")

register_exception_handlers(app)
app.include_router(catalogo.router)
app.include_router(estadisticas.router)
app.include_router(videojuegos.router)