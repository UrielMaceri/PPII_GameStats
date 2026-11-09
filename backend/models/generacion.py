from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .consola import Consola


class Generacion(Base):
    __tablename__ = "generaciones"
    __table_args__ = (
        CheckConstraint("numero BETWEEN 1 AND 9", name="ck_generaciones_numero"),
        CheckConstraint(
            "anio_inicio IS NULL OR anio_fin IS NULL OR anio_inicio <= anio_fin",
            name="ck_generaciones_rango_anios",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    numero: Mapped[int] = mapped_column(unique=True, nullable=False)
    anio_inicio: Mapped[int | None] = mapped_column(nullable=True)
    anio_fin: Mapped[int | None] = mapped_column(nullable=True)

    consolas: Mapped[list[Consola]] = relationship(back_populates="generacion")
