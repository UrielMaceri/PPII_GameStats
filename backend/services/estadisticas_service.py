from dataclasses import dataclass
from datetime import date

from sqlalchemy import extract, func, select
from sqlalchemy.orm import Session

from models.consola import Consola
from models.desarrollador import Desarrollador
from models.fabricante import Fabricante
from models.generacion import Generacion
from models.publisher import Publisher
from models.videojuego import Videojuego
from schemas.catalogo import ItemCatalogo
from schemas.estadisticas import (
    ConsolaMasVendida,
    FabricanteDominador,
    JuegoMasVendido,
    MetaEstadisticasVideojuegos,
    RankingDeveloper,
    RankingPublisher,
    ResumenVideojuegos,
    VentasPorAnio,
    VentasPorConsola,
    VentasPorFabricante,
    VentasPorGeneracion,
)


@dataclass(frozen=True)
class FiltrosEstadisticas:
    year_from: int | None = None
    year_to: int | None = None
    generation_id: int | None = None
    manufacturer_id: int | None = None
    console_id: int | None = None
    publisher_id: int | None = None

    def como_dict(self) -> dict[str, int]:
        values = {
            "yearFrom": self.year_from,
            "yearTo": self.year_to,
            "generationId": self.generation_id,
            "manufacturerId": self.manufacturer_id,
            "consoleId": self.console_id,
            "publisherId": self.publisher_id,
        }
        return {key: value for key, value in values.items() if value is not None}


class EstadisticasService:
    def __init__(self, session: Session) -> None:
        self.session = session

    @staticmethod
    def meta(filtros: FiltrosEstadisticas) -> MetaEstadisticasVideojuegos:
        return MetaEstadisticasVideojuegos(
            unit="million_copies",
            filters=filtros.como_dict(),
        )

    def resumen(self, filtros: FiltrosEstadisticas) -> ResumenVideojuegos:
        juegos = self._juegos_filtrados(filtros)
        game_count, total_sales = self.session.execute(
            select(
                func.count(juegos.c.game_id),
                func.coalesce(func.sum(juegos.c.sales), 0),
            )
        ).one()

        top = self.session.execute(
            select(
                juegos.c.console_id,
                juegos.c.console_name,
                func.sum(juegos.c.sales).label("sales"),
            )
            .where(juegos.c.sales.is_not(None))
            .group_by(juegos.c.console_id, juegos.c.console_name)
            .order_by(
                func.sum(juegos.c.sales).desc(),
                juegos.c.console_name.asc(),
                juegos.c.console_id.asc(),
            )
            .limit(1)
        ).first()

        return ResumenVideojuegos(
            game_count=game_count,
            total_sales=float(total_sales),
            top_console=(
                ConsolaMasVendida(
                    id=top.console_id,
                    name=top.console_name,
                    sales=float(top.sales),
                )
                if top is not None
                else None
            ),
        )

    def ventas_por_generacion(
        self, filtros: FiltrosEstadisticas
    ) -> list[VentasPorGeneracion]:
        juegos = self._juegos_filtrados(filtros)
        rows = self.session.execute(
            select(
                juegos.c.generation_id,
                juegos.c.generation_number,
                func.sum(juegos.c.sales).label("sales"),
            )
            .where(juegos.c.sales.is_not(None))
            .group_by(juegos.c.generation_id, juegos.c.generation_number)
            .order_by(juegos.c.generation_number)
        )
        return [
            VentasPorGeneracion(
                generation_id=row.generation_id,
                generation_number=row.generation_number,
                sales=float(row.sales),
            )
            for row in rows
        ]

    def ventas_por_consola(
        self, filtros: FiltrosEstadisticas
    ) -> list[VentasPorConsola]:
        juegos = self._juegos_filtrados(filtros)
        rows = self.session.execute(
            select(
                juegos.c.console_id,
                juegos.c.console_name,
                func.sum(juegos.c.sales).label("sales"),
            )
            .where(juegos.c.sales.is_not(None))
            .group_by(juegos.c.console_id, juegos.c.console_name)
            .order_by(
                func.sum(juegos.c.sales).desc(),
                juegos.c.console_name.asc(),
            )
        )
        return [
            VentasPorConsola(
                console_id=row.console_id,
                console_name=row.console_name,
                sales=float(row.sales),
            )
            for row in rows
        ]

    def ventas_por_fabricante(
        self, filtros: FiltrosEstadisticas
    ) -> list[VentasPorFabricante]:
        juegos = self._juegos_filtrados(filtros)
        rows = self.session.execute(
            select(
                juegos.c.manufacturer_id,
                juegos.c.manufacturer_name,
                func.sum(juegos.c.sales).label("sales"),
            )
            .where(juegos.c.sales.is_not(None))
            .group_by(juegos.c.manufacturer_id, juegos.c.manufacturer_name)
            .order_by(
                func.sum(juegos.c.sales).desc(),
                juegos.c.manufacturer_name.asc(),
            )
        )
        return [
            VentasPorFabricante(
                manufacturer_id=row.manufacturer_id,
                manufacturer_name=row.manufacturer_name,
                sales=float(row.sales),
            )
            for row in rows
        ]

    def ranking_publishers(
        self, filtros: FiltrosEstadisticas, limit: int
    ) -> list[RankingPublisher]:
        juegos = self._juegos_filtrados(filtros)
        rows = self.session.execute(
            select(
                juegos.c.publisher_id,
                juegos.c.publisher_name,
                func.sum(juegos.c.sales).label("sales"),
                func.count(juegos.c.game_id).label("game_count"),
            )
            .where(juegos.c.publisher_id.is_not(None))
            .group_by(juegos.c.publisher_id, juegos.c.publisher_name)
        ).all()
        rows.sort(
            key=lambda row: (
                row.sales is None,
                -float(row.sales) if row.sales is not None else 0,
                row.publisher_name.casefold(),
            )
        )
        return [
            RankingPublisher(
                publisher_id=row.publisher_id,
                publisher_name=row.publisher_name,
                sales=float(row.sales) if row.sales is not None else None,
                game_count=row.game_count,
            )
            for row in rows[:limit]
        ]

    def ranking_desarrolladores(
        self, filtros: FiltrosEstadisticas, limit: int
    ) -> list[RankingDeveloper]:
        juegos = self._juegos_filtrados(filtros)
        rows = self.session.execute(
            select(
                juegos.c.developer_id,
                juegos.c.developer_name,
                func.sum(juegos.c.sales).label("sales"),
                func.count(juegos.c.game_id).label("game_count"),
            )
            .where(juegos.c.developer_id.is_not(None))
            .group_by(juegos.c.developer_id, juegos.c.developer_name)
        ).all()
        rows.sort(
            key=lambda row: (
                row.sales is None,
                -float(row.sales) if row.sales is not None else 0,
                row.developer_name.casefold(),
            )
        )
        return [
            RankingDeveloper(
                developer_id=row.developer_id,
                developer_name=row.developer_name,
                sales=float(row.sales) if row.sales is not None else None,
                game_count=row.game_count,
            )
            for row in rows[:limit]
        ]

    def ventas_por_anio(
        self, filtros: FiltrosEstadisticas
    ) -> list[VentasPorAnio]:
        juegos = self._juegos_filtrados(filtros)
        release_year = extract("year", juegos.c.release_date)
        rows = self.session.execute(
            select(
                release_year.label("release_year"),
                func.sum(juegos.c.sales).label("sales"),
            )
            .where(
                juegos.c.release_date.is_not(None),
                juegos.c.sales.is_not(None),
            )
            .group_by(release_year)
            .order_by(release_year)
        )
        return [
            VentasPorAnio(
                release_year=row.release_year,
                sales=float(row.sales),
            )
            for row in rows
        ]

    def juegos_mas_vendidos(
        self, filtros: FiltrosEstadisticas, limit: int
    ) -> list[JuegoMasVendido]:
        juegos = self._juegos_filtrados(filtros)
        rows = self.session.execute(
            select(
                juegos.c.game_id,
                juegos.c.title,
                juegos.c.console_name,
                extract("year", juegos.c.release_date).label("release_year"),
                juegos.c.sales,
            )
            .where(juegos.c.sales.is_not(None))
            .order_by(
                juegos.c.sales.desc(),
                juegos.c.title.asc(),
                juegos.c.game_id.asc(),
            )
            .limit(limit)
        )
        return [
            JuegoMasVendido(
                game_id=row.game_id,
                title=row.title,
                console_name=row.console_name,
                release_year=(
                    int(row.release_year) if row.release_year is not None else None
                ),
                sales=float(row.sales),
            )
            for row in rows
        ]

    def dominador_por_generacion(
        self, filtros: FiltrosEstadisticas
    ) -> list[FabricanteDominador]:
        juegos = self._juegos_filtrados(filtros)
        rows = self.session.execute(
            select(
                juegos.c.generation_id,
                juegos.c.generation_number,
                juegos.c.manufacturer_id,
                juegos.c.manufacturer_name,
                func.sum(juegos.c.sales).label("sales"),
            )
            .where(juegos.c.sales.is_not(None))
            .group_by(
                juegos.c.generation_id,
                juegos.c.generation_number,
                juegos.c.manufacturer_id,
                juegos.c.manufacturer_name,
            )
            .order_by(
                juegos.c.generation_number,
                func.sum(juegos.c.sales).desc(),
                juegos.c.manufacturer_name.asc(),
            )
        )
        ganadores = {}
        for row in rows:
            ganadores.setdefault(row.generation_id, row)

        return [
            FabricanteDominador(
                generation_id=row.generation_id,
                generation_number=row.generation_number,
                manufacturer=ItemCatalogo(
                    id=row.manufacturer_id,
                    name=row.manufacturer_name,
                ),
                sales=float(row.sales),
            )
            for row in ganadores.values()
        ]

    @staticmethod
    def _juegos_filtrados(filtros: FiltrosEstadisticas):
        statement = (
            select(
                Videojuego.id.label("game_id"),
                Videojuego.titulo.label("title"),
                Videojuego.ventas.label("sales"),
                Videojuego.fecha_lanzamiento.label("release_date"),
                Consola.id.label("console_id"),
                Consola.nombre.label("console_name"),
                Generacion.id.label("generation_id"),
                Generacion.numero.label("generation_number"),
                Fabricante.id.label("manufacturer_id"),
                Fabricante.nombre.label("manufacturer_name"),
                Publisher.id.label("publisher_id"),
                Publisher.nombre.label("publisher_name"),
                Desarrollador.id.label("developer_id"),
                Desarrollador.nombre.label("developer_name"),
            )
            .join(Videojuego.consola)
            .join(Consola.fabricante)
            .join(Consola.generacion)
            .outerjoin(Videojuego.publisher)
            .outerjoin(Videojuego.desarrollador)
        )
        if filtros.year_from is not None:
            statement = statement.where(
                Videojuego.fecha_lanzamiento >= date(filtros.year_from, 1, 1)
            )
        if filtros.year_to is not None:
            statement = statement.where(
                Videojuego.fecha_lanzamiento <= date(filtros.year_to, 12, 31)
            )
        if filtros.generation_id is not None:
            statement = statement.where(Consola.generacion_id == filtros.generation_id)
        if filtros.manufacturer_id is not None:
            statement = statement.where(Consola.fabricante_id == filtros.manufacturer_id)
        if filtros.console_id is not None:
            statement = statement.where(Videojuego.consola_id == filtros.console_id)
        if filtros.publisher_id is not None:
            statement = statement.where(Videojuego.publisher_id == filtros.publisher_id)
        return statement.subquery()
