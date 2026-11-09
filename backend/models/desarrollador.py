from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .videojuego import Videojuego


class Desarrollador(Base):
    __tablename__ = "desarrolladores"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)

    videojuegos: Mapped[list[Videojuego]] = relationship(back_populates="desarrollador")
