from collections import defaultdict
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from data.database import get_session
from errors import SolicitudInvalidaError
from models.consola import Consola
from schemas.estadisticas import (
    FabricanteDominador,
    JuegoMasVendido,
    RankingDeveloper,
    RankingPublisher,
    RespuestaEstadistica,
    ResumenVideojuegos,
    VentasPorAnio,
    VentasPorConsola,
    VentasPorFabricante,
    VentasPorGeneracion,
)
from schemas.estadisticas import (
    ConsolaEstadistica,
    DatosEstadisticasConsolas,
    LanzamientosDecada,
    MetaEstadisticasConsolas,
    RespuestaEstadisticasConsolas,
    ResumenConsolas,
    VentasFabricante,
    VentasGeneracion,
)
from services.estadisticas_service import EstadisticasService, FiltrosEstadisticas

router = APIRouter(prefix="/api/estadisticas", tags=["Estadísticas"])


def get_estadisticas_service(
    session: Annotated[Session, Depends(get_session)],
) -> EstadisticasService:
    return EstadisticasService(session)


def get_filtros(
    year_from: Annotated[int | None, Query(alias="yearFrom", ge=1000, le=9999)] = None,
    year_to: Annotated[int | None, Query(alias="yearTo", ge=1000, le=9999)] = None,
    generation_id: Annotated[int | None, Query(alias="generationId", gt=0)] = None,
    manufacturer_id: Annotated[int | None, Query(alias="manufacturerId", gt=0)] = None,
    console_id: Annotated[int | None, Query(alias="consoleId", gt=0)] = None,
    publisher_id: Annotated[int | None, Query(alias="publisherId", gt=0)] = None,
) -> FiltrosEstadisticas:
    if year_from is not None and year_to is not None and year_from > year_to:
        raise SolicitudInvalidaError(
            "La solicitud contiene parámetros inválidos.",
            [{"field": "yearFrom", "message": "No puede ser mayor que yearTo."}],
        )
    return FiltrosEstadisticas(
        year_from=year_from,
        year_to=year_to,
        generation_id=generation_id,
        manufacturer_id=manufacturer_id,
        console_id=console_id,
        publisher_id=publisher_id,
    )


EstadisticasDep = Annotated[EstadisticasService, Depends(get_estadisticas_service)]
FiltrosDep = Annotated[FiltrosEstadisticas, Depends(get_filtros)]


@router.get(
    "/consolas",
    response_model=RespuestaEstadisticasConsolas,
    summary="Estadísticas basadas en consolas",
)
def estadisticas_consolas(
    session: Annotated[Session, Depends(get_session)],
) -> RespuestaEstadisticasConsolas:
    consolas = session.scalars(
        select(Consola).options(
            joinedload(Consola.fabricante),
            joinedload(Consola.generacion),
        )
    ).all()

    ventas_fabricante: dict[str, float] = defaultdict(float)
    cantidad_fabricante: dict[str, int] = defaultdict(int)
    ventas_generacion: dict[int, float] = defaultdict(float)
    cantidad_generacion: dict[int, int] = defaultdict(int)
    lanzamientos_decada: dict[int, int] = defaultdict(int)
    ventas_totales = 0.0
    consolas_con_ventas: list[ConsolaEstadistica] = []

    for consola in consolas:
        fabricante = consola.fabricante.nombre
        generacion = consola.generacion.numero
        cantidad_fabricante[fabricante] += 1
        cantidad_generacion[generacion] += 1

        ventas = (
            float(consola.unidades_vendidas)
            if consola.unidades_vendidas is not None
            else None
        )
        if ventas is not None:
            ventas_totales += ventas
            ventas_fabricante[fabricante] += ventas
            ventas_generacion[generacion] += ventas
            consolas_con_ventas.append(
                ConsolaEstadistica(
                    id=consola.id,
                    name=consola.nombre,
                    sales=ventas,
                    manufacturer_id=consola.fabricante_id,
                    manufacturer=fabricante,
                    generation_id=consola.generacion_id,
                    generation=generacion,
                    release_year=consola.anio_lanzamiento,
                )
            )

        if consola.anio_lanzamiento is not None:
            decade = consola.anio_lanzamiento // 10 * 10
            lanzamientos_decada[decade] += 1

    consolas_con_ventas.sort(key=lambda item: (-item.sales, item.name))
    fabricantes = [
        VentasFabricante(
            name=name,
            sales=sales,
            console_count=cantidad_fabricante[name],
        )
        for name, sales in ventas_fabricante.items()
    ]
    fabricantes.sort(key=lambda item: (-item.sales, item.name))

    generaciones = [
        VentasGeneracion(
            name=f"Generación {number}",
            sales=sales,
            console_count=cantidad_generacion[number],
        )
        for number, sales in ventas_generacion.items()
    ]
    generaciones.sort(key=lambda item: int(item.name.split()[-1]))

    decades = [
        LanzamientosDecada(decade=f"{year}s", console_count=count)
        for year, count in sorted(lanzamientos_decada.items())
    ]

    data = DatosEstadisticasConsolas(
        summary=ResumenConsolas(
            console_count=len(consolas),
            manufacturer_count=len(cantidad_fabricante),
            generation_count=len(cantidad_generacion),
            total_sales=ventas_totales,
        ),
        consoles=consolas_con_ventas,
        sales_by_manufacturer=fabricantes,
        sales_by_generation=generaciones,
        releases_by_decade=decades,
    )
    return RespuestaEstadisticasConsolas(
        data=data,
        meta=MetaEstadisticasConsolas(
            unit="million_units",
            release_year_basis="console_release_year",
        ),
    )


@router.get("/resumen", response_model=RespuestaEstadistica[ResumenVideojuegos])
def resumen_videojuegos(service: EstadisticasDep, filtros: FiltrosDep):
    return RespuestaEstadistica[ResumenVideojuegos](
        data=service.resumen(filtros),
        meta=service.meta(filtros),
    )


@router.get(
    "/ventas-por-generacion",
    response_model=RespuestaEstadistica[list[VentasPorGeneracion]],
)
def ventas_por_generacion(service: EstadisticasDep, filtros: FiltrosDep):
    return RespuestaEstadistica[list[VentasPorGeneracion]](
        data=service.ventas_por_generacion(filtros),
        meta=service.meta(filtros),
    )


@router.get(
    "/ventas-por-consola",
    response_model=RespuestaEstadistica[list[VentasPorConsola]],
)
def ventas_por_consola(service: EstadisticasDep, filtros: FiltrosDep):
    return RespuestaEstadistica[list[VentasPorConsola]](
        data=service.ventas_por_consola(filtros),
        meta=service.meta(filtros),
    )


@router.get(
    "/ventas-por-fabricante",
    response_model=RespuestaEstadistica[list[VentasPorFabricante]],
)
def ventas_por_fabricante(service: EstadisticasDep, filtros: FiltrosDep):
    return RespuestaEstadistica[list[VentasPorFabricante]](
        data=service.ventas_por_fabricante(filtros),
        meta=service.meta(filtros),
    )


@router.get(
    "/ranking-publishers",
    response_model=RespuestaEstadistica[list[RankingPublisher]],
)
def ranking_publishers(
    service: EstadisticasDep,
    filtros: FiltrosDep,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
):
    return RespuestaEstadistica[list[RankingPublisher]](
        data=service.ranking_publishers(filtros, limit),
        meta=service.meta(filtros),
    )


@router.get(
    "/ranking-desarrolladores",
    response_model=RespuestaEstadistica[list[RankingDeveloper]],
)
def ranking_desarrolladores(
    service: EstadisticasDep,
    filtros: FiltrosDep,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
):
    return RespuestaEstadistica[list[RankingDeveloper]](
        data=service.ranking_desarrolladores(filtros, limit),
        meta=service.meta(filtros),
    )


@router.get(
    "/ventas-por-anio",
    response_model=RespuestaEstadistica[list[VentasPorAnio]],
)
def ventas_por_anio(service: EstadisticasDep, filtros: FiltrosDep):
    return RespuestaEstadistica[list[VentasPorAnio]](
        data=service.ventas_por_anio(filtros),
        meta=service.meta(filtros),
    )


@router.get(
    "/juegos-mas-vendidos",
    response_model=RespuestaEstadistica[list[JuegoMasVendido]],
)
def juegos_mas_vendidos(
    service: EstadisticasDep,
    filtros: FiltrosDep,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
):
    return RespuestaEstadistica[list[JuegoMasVendido]](
        data=service.juegos_mas_vendidos(filtros, limit),
        meta=service.meta(filtros),
    )


@router.get(
    "/dominador-por-generacion",
    response_model=RespuestaEstadistica[list[FabricanteDominador]],
)
def dominador_por_generacion(service: EstadisticasDep, filtros: FiltrosDep):
    return RespuestaEstadistica[list[FabricanteDominador]](
        data=service.dominador_por_generacion(filtros),
        meta=service.meta(filtros),
    )
