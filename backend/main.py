from fastapi import FastAPI

from errors import register_exception_handlers
from routers import catalogo

app = FastAPI(title="GameStats API")

register_exception_handlers(app)
app.include_router(catalogo.router)