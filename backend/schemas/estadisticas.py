from typing import Generic, TypeVar

from schemas.base import CamelModel
from schemas.catalogo import ItemCatalogo

ContenidoEstadistica = TypeVar("ContenidoEstadistica")


class ConsolaEstadistica(CamelModel):
    id: int
    name: str
    sales: float
    manufacturer_id: int
    manufacturer: str
    generation_id: int
    generation: int
    release_year: int | None


class VentasFabricante(CamelModel):
    name: str
    sales: float
    console_count: int


class VentasGeneracion(CamelModel):
    name: str
    sales: float
    console_count: int


class LanzamientosDecada(CamelModel):
    decade: str
    console_count: int


class ResumenConsolas(CamelModel):
    console_count: int
    manufacturer_count: int
    generation_count: int
    total_sales: float


class DatosEstadisticasConsolas(CamelModel):
    summary: ResumenConsolas
    consoles: list[ConsolaEstadistica]
    sales_by_manufacturer: list[VentasFabricante]
    sales_by_generation: list[VentasGeneracion]
    releases_by_decade: list[LanzamientosDecada]


class MetaEstadisticasConsolas(CamelModel):
    unit: str
    release_year_basis: str


class RespuestaEstadisticasConsolas(CamelModel):
    data: DatosEstadisticasConsolas
    meta: MetaEstadisticasConsolas


class MetaEstadisticasVideojuegos(CamelModel):
    unit: str
    filters: dict[str, int]


class RespuestaEstadistica(CamelModel, Generic[ContenidoEstadistica]):
    data: ContenidoEstadistica
    meta: MetaEstadisticasVideojuegos


class ConsolaMasVendida(CamelModel):
    id: int
    name: str
    sales: float


class ResumenVideojuegos(CamelModel):
    game_count: int
    total_sales: float
    top_console: ConsolaMasVendida | None


class VentasPorGeneracion(CamelModel):
    generation_id: int
    generation_number: int
    sales: float


class VentasPorConsola(CamelModel):
    console_id: int
    console_name: str
    sales: float


class VentasPorFabricante(CamelModel):
    manufacturer_id: int
    manufacturer_name: str
    sales: float


class RankingPublisher(CamelModel):
    publisher_id: int
    publisher_name: str
    sales: float | None
    game_count: int


class RankingDeveloper(CamelModel):
    developer_id: int
    developer_name: str
    sales: float | None
    game_count: int


class VentasPorAnio(CamelModel):
    release_year: int
    sales: float


class JuegoMasVendido(CamelModel):
    game_id: int
    title: str
    console_name: str
    release_year: int | None
    sales: float


class FabricanteDominador(CamelModel):
    generation_id: int
    generation_number: int
    manufacturer: ItemCatalogo
    sales: float
