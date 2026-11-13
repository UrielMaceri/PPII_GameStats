from collections.abc import Iterable
from typing import Protocol

from schemas.base import CamelModel


class _ConNombre(Protocol):
    id: int
    nombre: str


class ItemCatalogo(CamelModel):
    id: int
    name: str


class RespuestaItems(CamelModel):
    data: list[ItemCatalogo]


def a_items(objetos: Iterable[_ConNombre]) -> RespuestaItems:
    return RespuestaItems(data=[ItemCatalogo(id=o.id, name=o.nombre) for o in objetos])