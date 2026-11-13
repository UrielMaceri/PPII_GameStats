from collections.abc import Sequence
from datetime import date

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from errors import ConflictError, NotFoundError, SolicitudInvalidaError, ValidacionError
from models.consola import Consola
from models.desarrollador import Desarrollador
from models.publisher import Publisher
from models.videojuego import Videojuego
from repositories.catalogo_repository import CatalogoRepository
from repositories.videojuego_repository import VideojuegoRepository
from schemas.videojuego import VideojuegoCreate, VideojuegoUpdate


class VideojuegoService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repo = VideojuegoRepository(session)
        self.catalogo = CatalogoRepository(session)

    # ---------- consultas ----------
    def listar(
        self,
        *,
        search: str | None,
        consola_id: int | None,
        publisher_id: int | None,
        year_from: int | None,
        year_to: int | None,
        page: int,
        page_size: int,
    ) -> tuple[Sequence[Videojuego], int]:
        if year_from is not None and year_to is not None and year_from > year_to:
            raise SolicitudInvalidaError(
                "La solicitud contiene parámetros inválidos.",
                [{"field": "yearFrom", "message": "No puede ser mayor que yearTo."}],
            )
        return self.repo.listar(
            search=search,
            consola_id=consola_id,
            publisher_id=publisher_id,
            year_from=year_from,
            year_to=year_to,
            offset=(page - 1) * page_size,
            limit=page_size,
        )

    def obtener(self, id_: int) -> Videojuego:
        videojuego = self.repo.obtener(id_)
        if videojuego is None:
            raise NotFoundError(f"No existe un videojuego con id {id_}.")
        return videojuego

    # ---------- escritura ----------
    def crear(self, datos: VideojuegoCreate) -> Videojuego:
        self._validar(datos)
        videojuego = Videojuego()
        self._aplicar(videojuego, datos)
        self.repo.agregar(videojuego)
        self._commit()
        return self.obtener(videojuego.id)

    def actualizar(self, id_: int, datos: VideojuegoUpdate) -> Videojuego:
        videojuego = self.obtener(id_)
        self._validar(datos, excluir_id=id_)
        self._aplicar(videojuego, datos)
        self._commit()
        return self.obtener(id_)

    def eliminar(self, id_: int) -> None:
        # Baja FÍSICA. Si el equipo decide baja lógica hay que agregar una
        # columna (p. ej. `activo`) al modelo y filtrar en el repositorio.
        videojuego = self.obtener(id_)
        self.repo.eliminar(videojuego)
        self._commit()

    # ---------- internos ----------
    @staticmethod
    def _aplicar(v: Videojuego, d: VideojuegoCreate | VideojuegoUpdate) -> None:
        v.titulo = d.title
        v.consola_id = d.console_id
        v.publisher_id = d.publisher_id
        v.desarrollador_id = d.developer_id
        # Contrato: solo año. El modelo tiene Date -> se guarda el 1 de enero.
        v.fecha_lanzamiento = date(d.release_year, 1, 1) if d.release_year else None
        v.ventas = d.sales

    def _validar(
        self, d: VideojuegoCreate | VideojuegoUpdate, excluir_id: int | None = None
    ) -> None:
        errores = []
        if not self.catalogo.existe(Consola, d.console_id):
            errores.append({"field": "consoleId", "message": f"No existe una consola con id {d.console_id}."})
        if d.publisher_id is not None and not self.catalogo.existe(Publisher, d.publisher_id):
            errores.append({"field": "publisherId", "message": f"No existe un publisher con id {d.publisher_id}."})
        if d.developer_id is not None and not self.catalogo.existe(Desarrollador, d.developer_id):
            errores.append({"field": "developerId", "message": f"No existe un desarrollador con id {d.developer_id}."})
        if errores:
            raise ValidacionError("Hay campos que requieren corrección.", errores)

        if self.repo.buscar_duplicado(d.title, d.console_id, excluir_id):
            raise ConflictError(
                "Ya existe un videojuego con ese título en esa consola.",
                [{"field": "title", "message": "Título duplicado para la consola elegida."}],
            )

    def _commit(self) -> None:
        try:
            self.session.commit()
        except IntegrityError as exc:  # red de seguridad (carreras, FKs, CHECK)
            self.session.rollback()
            raise ConflictError(
                "No se pudo guardar: viola una restricción de la base de datos."
            ) from exc