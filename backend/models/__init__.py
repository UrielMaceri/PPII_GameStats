"""SQLAlchemy models for the GameStats domain."""

from .base import Base
from .consola import Consola
from .desarrollador import Desarrollador
from .fabricante import Fabricante
from .generacion import Generacion
from .publisher import Publisher
from .videojuego import Videojuego

__all__ = [
    "Base",
    "Consola",
    "Desarrollador",
    "Fabricante",
    "Generacion",
    "Publisher",
    "Videojuego",
]
