from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from data.database import get_session
from schemas.videojuego import (
    Paginacion,
    RespuestaVideojuego,
    RespuestaVideojuegos,
    VideojuegoCreate,
    VideojuegoUpdate,
    a_videojuego_out,
)
from services.videojuego_service import VideojuegoService

router = APIRouter(prefix="/api/videojuegos", tags=["Videojuegos"])

_400 = {400: {"description": "INVALID_REQUEST: parámetros inválidos"}}
_404 = {404: {"description": "NOT_FOUND: el videojuego no existe"}}
_409 = {409: {"description": "DUPLICATE_RESOURCE: título duplicado en la misma consola"}}
_422 = {422: {"description": "VALIDATION_ERROR: campos inválidos o relaciones inexistentes"}}


def get_videojuego_service(
    session: Annotated[Session, Depends(get_session)],
) -> VideojuegoService:
    return VideojuegoService(session)


ServiceDep = Annotated[VideojuegoService, Depends(get_videojuego_service)]


@router.get(
    "", response_model=RespuestaVideojuegos, responses=_400, summary="Listar videojuegos"
)
def listar(
    service: ServiceDep,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="pageSize", ge=1, le=100)] = 20,
    search: Annotated[str | None, Query(max_length=255, description="Búsqueda parcial por título")] = None,
    console_id: Annotated[int | None, Query(alias="consoleId", gt=0)] = None,
    publisher_id: Annotated[int | None, Query(alias="publisherId", gt=0)] = None,
    year_from: Annotated[int | None, Query(alias="yearFrom", ge=1000, le=9999)] = None,
    year_to: Annotated[int | None, Query(alias="yearTo", ge=1000, le=9999)] = None,
):
    items, total = service.listar(
        search=search,
        consola_id=console_id,
        publisher_id=publisher_id,
        year_from=year_from,
        year_to=year_to,
        page=page,
        page_size=page_size,
    )
    return RespuestaVideojuegos(
        data=[a_videojuego_out(v) for v in items],
        pagination=Paginacion(
            page=page,
            page_size=page_size,
            total_items=total,
            total_pages=(total + page_size - 1) // page_size,
        ),
    )


@router.get(
    "/{id}", response_model=RespuestaVideojuego, responses={**_400, **_404}, summary="Detalle"
)
def obtener(id: int, service: ServiceDep):
    return RespuestaVideojuego(data=a_videojuego_out(service.obtener(id)))


@router.post(
    "",
    response_model=RespuestaVideojuego,
    status_code=status.HTTP_201_CREATED,
    responses={**_409, **_422},
    summary="Crear videojuego",
)
def crear(datos: VideojuegoCreate, service: ServiceDep):
    return RespuestaVideojuego(data=a_videojuego_out(service.crear(datos)))


@router.put(
    "/{id}",
    response_model=RespuestaVideojuego,
    responses={**_400, **_404, **_409, **_422},
    summary="Modificar videojuego (objeto completo)",
)
def actualizar(id: int, datos: VideojuegoUpdate, service: ServiceDep):
    return RespuestaVideojuego(data=a_videojuego_out(service.actualizar(id, datos)))


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={**_400, **_404},
    summary="Eliminar videojuego",
)
def eliminar(id: int, service: ServiceDep):
    service.eliminar(id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)