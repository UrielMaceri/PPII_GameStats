from pydantic import Field, field_validator

from models.videojuego import Videojuego
from schemas.base import CamelModel
from schemas.catalogo import ItemCatalogo


class _VideojuegoEntrada(CamelModel):
    title: str = Field(min_length=1, max_length=255, examples=["Super Mario 64"])
    console_id: int = Field(gt=0, examples=[12])

    @field_validator("title")
    @classmethod
    def _limpiar_titulo(cls, v: str) -> str:
        v = " ".join(v.split())  # recorta y colapsa espacios
        if not v:
            raise ValueError("El título no puede estar vacío.")
        return v


class VideojuegoCreate(_VideojuegoEntrada):
    """POST: los campos opcionales se pueden omitir o enviar como null."""

    publisher_id: int | None = Field(default=None, gt=0)
    developer_id: int | None = Field(default=None, gt=0)
    release_year: int | None = Field(default=None, ge=1000, le=9999)
    sales: float | None = Field(default=None, ge=0)


class VideojuegoUpdate(_VideojuegoEntrada):
    """PUT: objeto completo; lo que quede vacío se envía explícitamente como null."""

    publisher_id: int | None = Field(gt=0)
    developer_id: int | None = Field(gt=0)
    release_year: int | None = Field(ge=1000, le=9999)
    sales: float | None = Field(ge=0)


class VideojuegoOut(CamelModel):
    id: int
    title: str
    console: ItemCatalogo
    publisher: ItemCatalogo | None
    developer: ItemCatalogo | None
    release_year: int | None
    sales: float | None


class Paginacion(CamelModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int


class RespuestaVideojuego(CamelModel):
    data: VideojuegoOut


class RespuestaVideojuegos(CamelModel):
    data: list[VideojuegoOut]
    pagination: Paginacion


def a_videojuego_out(v: Videojuego) -> VideojuegoOut:
    return VideojuegoOut(
        id=v.id,
        title=v.titulo,
        console=ItemCatalogo(id=v.consola.id, name=v.consola.nombre),
        publisher=(
            ItemCatalogo(id=v.publisher.id, name=v.publisher.nombre) if v.publisher else None
        ),
        developer=(
            ItemCatalogo(id=v.desarrollador.id, name=v.desarrollador.nombre)
            if v.desarrollador
            else None
        ),
        # El modelo guarda fecha completa; el contrato expone solo el año.
        release_year=v.fecha_lanzamiento.year if v.fecha_lanzamiento else None,
        sales=float(v.ventas) if v.ventas is not None else None,
    )