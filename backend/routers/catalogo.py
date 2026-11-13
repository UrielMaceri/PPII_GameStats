from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from data.database import get_session
from schemas.catalogo import RespuestaItems, a_items
from services.catalogo_service import CatalogoService

router = APIRouter(prefix="/api", tags=["Catálogo auxiliar"])


def get_catalogo_service(
    session: Annotated[Session, Depends(get_session)],
) -> CatalogoService:
    return CatalogoService(session)


ServiceDep = Annotated[CatalogoService, Depends(get_catalogo_service)]


@router.get("/consolas", response_model=RespuestaItems, summary="Consolas (selector)")
def listar_consolas(service: ServiceDep):
    return a_items(service.consolas())


@router.get("/publishers", response_model=RespuestaItems, summary="Publishers (selector)")
def listar_publishers(service: ServiceDep):
    return a_items(service.publishers())


@router.get(
    "/desarrolladores", response_model=RespuestaItems, summary="Desarrolladores (selector)"
)
def listar_desarrolladores(service: ServiceDep):
    return a_items(service.desarrolladores())