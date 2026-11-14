from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .consola import Consola
    from .desarrollador import Desarrollador
    from .publisher import Publisher


class Videojuego(Base):
    __tablename__ = "videojuegos"
    __table_args__ = (
        UniqueConstraint("titulo", "consola_id", name="uq_videojuegos_titulo_consola"),
        CheckConstraint(
            "ventas IS NULL OR ventas >= 0", name="ck_videojuegos_ventas_no_negativas"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str] = mapped_column(String(255), nullable=False)
    consola_id: Mapped[int] = mapped_column(ForeignKey("consolas.id"), nullable=False)
    publisher_id: Mapped[int | None] = mapped_column(
        ForeignKey("publishers.id"), nullable=True
    )
    desarrollador_id: Mapped[int | None] = mapped_column(
        ForeignKey("desarrolladores.id"), nullable=True
    )
    fecha_lanzamiento: Mapped[date | None] = mapped_column(Date, nullable=True)
    ventas: Mapped[Decimal | None] = mapped_column(Numeric(14, 4), nullable=True)
    imagen_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)

    consola: Mapped[Consola] = relationship(back_populates="videojuegos")
    publisher: Mapped[Publisher | None] = relationship(back_populates="videojuegos")
    desarrollador: Mapped[Desarrollador | None] = relationship(
        back_populates="videojuegos"
    )
