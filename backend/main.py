from fastapi import FastAPI

from errors import register_exception_handlers

app = FastAPI(title="GameStats API")

register_exception_handlers(app)