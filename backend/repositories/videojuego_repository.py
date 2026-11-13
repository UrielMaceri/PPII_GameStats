from collections.abc import Sequence
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from models.videojuego import Videojuego

_CARGA = (
    joinedload(Videojuego.consola),
    joinedload(Videojuego.publisher),
    joinedload(Videojuego.desarrollador),
)


class VideojuegoRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def listar(
        self,
        *,
        search: str | None,
        consola_id: int | None,
        publisher_id: int | None,
        year_from: int | None,
        year_to: int | None,
        offset: int,
        limit: int,
    ) -> tuple[Sequence[Videojuego], int]:
        condiciones = []
        if search:
            condiciones.append(Videojuego.titulo.icontains(search, autoescape=True))
        if consola_id is not None:
            condiciones.append(Videojuego.consola_id == consola_id)
        if publisher_id is not None:
            condiciones.append(Videojuego.publisher_id == publisher_id)
        if year_from is not None:
            condiciones.append(Videojuego.fecha_lanzamiento >= date(year_from, 1, 1))
        if year_to is not None:
            condiciones.append(Videojuego.fecha_lanzamiento <= date(year_to, 12, 31))

        total = self.session.scalar(
            select(func.count()).select_from(Videojuego).where(*condiciones)
        )
        items = (
            self.session.scalars(
                select(Videojuego)
                .where(*condiciones)
                .options(*_CARGA)
                .order_by(Videojuego.titulo, Videojuego.id)
                .offset(offset)
                .limit(limit)
            )
            .unique()
            .all()
        )
        return items, total or 0

    def obtener(self, id_: int) -> Videojuego | None:
        return self.session.scalars(
            select(Videojuego)
            .where(Videojuego.id == id_)
            .options(*_CARGA)
            .execution_options(populate_existing=True)
        ).unique().first()

    def buscar_duplicado(
        self, titulo: str, consola_id: int, excluir_id: int | None = None
    ) -> Videojuego | None:
        stmt = select(Videojuego).where(
            func.lower(Videojuego.titulo) == titulo.lower(),
            Videojuego.consola_id == consola_id,
        )
        if excluir_id is not None:
            stmt = stmt.where(Videojuego.id != excluir_id)
        return self.session.scalars(stmt).first()

    def agregar(self, videojuego: Videojuego) -> None:
        self.session.add(videojuego)
        self.session.flush()  # autoflush=False: así obtenemos el id

    def eliminar(self, videojuego: Videojuego) -> None:
        self.session.delete(videojuego)