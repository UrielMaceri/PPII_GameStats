from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.consola import Consola
from models.desarrollador import Desarrollador
from models.publisher import Publisher


class CatalogoRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def listar_consolas(self) -> Sequence[Consola]:
        return self.session.scalars(select(Consola).order_by(Consola.nombre)).all()

    def listar_publishers(self) -> Sequence[Publisher]:
        return self.session.scalars(select(Publisher).order_by(Publisher.nombre)).all()

    def listar_desarrolladores(self) -> Sequence[Desarrollador]:
        return self.session.scalars(
            select(Desarrollador).order_by(Desarrollador.nombre)
        ).all()

    def existe(self, modelo: type, id_: int) -> bool:
        return self.session.get(modelo, id_) is not None