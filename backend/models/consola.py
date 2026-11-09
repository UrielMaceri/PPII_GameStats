from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .fabricante import Fabricante
    from .generacion import Generacion
    from .videojuego import Videojuego


class Consola(Base):
    __tablename__ = "consolas"
    __table_args__ = (
        CheckConstraint(
            "unidades_vendidas IS NULL OR unidades_vendidas >= 0",
            name="ck_consolas_unidades_no_negativas",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    fabricante_id: Mapped[int] = mapped_column(
        ForeignKey("fabricantes.id"), nullable=False
    )
    generacion_id: Mapped[int] = mapped_column(
        ForeignKey("generaciones.id"), nullable=False
    )
    fecha_lanzamiento: Mapped[date | None] = mapped_column(Date, nullable=True)
    unidades_vendidas: Mapped[float | None] = mapped_column(Numeric(14, 4), nullable=True)

    fabricante: Mapped[Fabricante] = relationship(back_populates="consolas")
    generacion: Mapped[Generacion] = relationship(back_populates="consolas")
    videojuegos: Mapped[list[Videojuego]] = relationship(back_populates="consola")
