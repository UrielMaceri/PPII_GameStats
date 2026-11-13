from collections.abc import Sequence

from sqlalchemy.orm import Session

from models.consola import Consola
from models.desarrollador import Desarrollador
from models.publisher import Publisher
from repositories.catalogo_repository import CatalogoRepository


class CatalogoService:
    def __init__(self, session: Session) -> None:
        self.repo = CatalogoRepository(session)

    def consolas(self) -> Sequence[Consola]:
        return self.repo.listar_consolas()

    def publishers(self) -> Sequence[Publisher]:
        return self.repo.listar_publishers()

    def desarrolladores(self) -> Sequence[Desarrollador]:
        return self.repo.listar_desarrolladores()