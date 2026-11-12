from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
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
    tipo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    fabricante_id: Mapped[int] = mapped_column(
        ForeignKey("fabricantes.id"), nullable=False
    )
    generacion_id: Mapped[int] = mapped_column(
        ForeignKey("generaciones.id"), nullable=False
    )
    anio_lanzamiento: Mapped[int | None] = mapped_column(Integer, nullable=True)
    anio_descontinuacion: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sigue_en_produccion: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    unidades_vendidas: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 4), nullable=True
    )
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    gif_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)

    fabricante: Mapped[Fabricante] = relationship(back_populates="consolas")
    generacion: Mapped[Generacion] = relationship(back_populates="consolas")
    videojuegos: Mapped[list[Videojuego]] = relationship(back_populates="consola")
