from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .consola import Consola


class Fabricante(Base):
    __tablename__ = "fabricantes"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    pais: Mapped[str | None] = mapped_column(String(100), nullable=True)

    consolas: Mapped[list[Consola]] = relationship(back_populates="fabricante")
