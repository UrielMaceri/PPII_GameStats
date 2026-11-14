from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import TypeVar

from sqlalchemy import inspect, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from data.database import SessionLocal, engine
from models import Base, Consola, Desarrollador, Publisher, Videojuego

CSV_PATH = Path(__file__).resolve().parent / "docs" / "scrapped_data.csv"

REQUIRED_COLUMNS = {
    "Game Name",
    "System Full",
    "Units(m)",
    "Publisher",
    "Developer",
    "Image_URL",
    "Release Date",
}
UNKNOWN_NAMES = {"unknown", "n/a"}
NameModel = TypeVar("NameModel", Publisher, Desarrollador)


@dataclass(frozen=True)
class GameRow:
    line: int
    title: str
    console_name: str
    sales: Decimal | None
    publisher: str | None
    developer: str | None
    image_url: str | None
    release_date: date | None


def _normalize_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = " ".join(value.split())
    return normalized or None


def _required_text(row: dict[str, str | None], column: str, line: int) -> str:
    value = _normalize_text(row.get(column))
    if value is None:
        raise ValueError(f"Fila {line}: falta el valor obligatorio '{column}'.")
    return value


def _optional_text(row: dict[str, str | None], column: str) -> str | None:
    value = _normalize_text(row.get(column))
    if value is None or value.casefold() in UNKNOWN_NAMES:
        return None
    return value


def _parse_sales(row: dict[str, str | None], line: int) -> Decimal | None:
    value = _optional_text(row, "Units(m)")
    if value is None:
        return None
    try:
        sales = Decimal(value)
    except InvalidOperation as error:
        raise ValueError(
            f"Fila {line}: ventas inválidas en 'Units(m)': {value!r}."
        ) from error
    if not sales.is_finite() or sales < 0:
        raise ValueError(f"Fila {line}: las ventas deben ser finitas y no negativas.")
    return None if sales == 0 else sales


def _parse_release_date(row: dict[str, str | None], line: int) -> date | None:
    value = _optional_text(row, "Release Date")
    if value is None:
        return None
    try:
        return datetime.strptime(value, "%d/%m/%Y").date()
    except ValueError as error:
        raise ValueError(
            f"Fila {line}: fecha inválida en 'Release Date': {value!r}; "
            "se esperaba DD/MM/AAAA."
        ) from error


def _parse_row(row: dict[str, str | None], line: int) -> GameRow:
    return GameRow(
        line=line,
        title=_required_text(row, "Game Name", line),
        console_name=_required_text(row, "System Full", line),
        sales=_parse_sales(row, line),
        publisher=_optional_text(row, "Publisher"),
        developer=_optional_text(row, "Developer"),
        image_url=_optional_text(row, "Image_URL"),
        release_date=_parse_release_date(row, line),
    )


def _completeness(row: GameRow) -> int:
    return sum(
        value is not None
        for value in (row.sales, row.publisher, row.developer, row.image_url)
    )


def _select_canonical(rows: list[GameRow]) -> GameRow:
    dated_rows = [row for row in rows if row.release_date is not None]
    if dated_rows:
        earliest_date = min(row.release_date for row in dated_rows)
        candidates = [row for row in dated_rows if row.release_date == earliest_date]
    else:
        candidates = rows

    return max(
        candidates,
        key=lambda row: (
            _completeness(row),
            row.sales if row.sales is not None else Decimal("-1"),
            -row.line,
        ),
    )


def _load_rows(csv_path: Path) -> tuple[dict[tuple[str, str], GameRow], int, int]:
    grouped: dict[tuple[str, str], list[GameRow]] = defaultdict(list)

    with csv_path.open(encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        missing_columns = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(f"Faltan columnas requeridas en el CSV: {missing}.")

        row_count = 0
        for line, row in enumerate(reader, start=2):
            parsed = _parse_row(row, line)
            key = (parsed.title.casefold(), parsed.console_name.casefold())
            grouped[key].append(parsed)
            row_count += 1

    if row_count == 0:
        raise ValueError("El CSV no contiene filas para importar.")

    canonical = {key: _select_canonical(rows) for key, rows in grouped.items()}
    duplicate_groups = sum(len(rows) > 1 for rows in grouped.values())
    ignored_rows = row_count - len(canonical)
    return canonical, duplicate_groups, ignored_rows


def _ensure_schema(database_engine: Engine) -> None:
    Base.metadata.create_all(database_engine)

    columns = {
        column["name"]
        for column in inspect(database_engine).get_columns("videojuegos")
    }
    if "imagen_url" not in columns:
        with database_engine.begin() as connection:
            connection.exec_driver_sql(
                "ALTER TABLE videojuegos ADD COLUMN imagen_url VARCHAR(2048)"
            )


def _load_name_cache(
    session: Session, model: type[NameModel]
) -> dict[str, NameModel]:
    cache: dict[str, NameModel] = {}
    for item in session.scalars(select(model).order_by(model.id)):
        cache.setdefault(item.nombre.casefold(), item)
    return cache


def _get_or_create_name(
    session: Session,
    model: type[NameModel],
    name: str | None,
    cache: dict[str, NameModel],
) -> NameModel | None:
    if name is None:
        return None
    key = name.casefold()
    item = cache.get(key)
    if item is None:
        item = model(nombre=name)
        session.add(item)
        cache[key] = item
    return item


def import_games(csv_path: Path = CSV_PATH) -> tuple[int, int, int, int]:
    _ensure_schema(engine)
    games, duplicate_groups, ignored_rows = _load_rows(csv_path)

    created = 0
    updated = 0
    with SessionLocal.begin() as session:
        consoles = {
            console.nombre.casefold(): console
            for console in session.scalars(select(Consola).order_by(Consola.id))
        }
        publishers = _load_name_cache(session, Publisher)
        developers = _load_name_cache(session, Desarrollador)

        existing_games: dict[tuple[str, int], Videojuego] = {}
        for videojuego in session.scalars(select(Videojuego).order_by(Videojuego.id)):
            key = (videojuego.titulo.casefold(), videojuego.consola_id)
            if key in existing_games:
                raise ValueError(
                    "La base ya contiene más de un videojuego con el mismo título "
                    f"y consola: {videojuego.titulo!r}."
                )
            existing_games[key] = videojuego

        for (title_key, console_name_key), row in games.items():
            console = consoles.get(console_name_key)
            if console is None:
                raise ValueError(
                    f"Fila {row.line}: no existe la consola {row.console_name!r}. "
                    "Ejecuta primero el importador de consolas."
                )

            key = (title_key, console.id)
            videojuego = existing_games.get(key)
            if videojuego is None:
                videojuego = Videojuego(titulo=row.title, consola=console)
                existing_games[key] = videojuego
                session.add(videojuego)
                created += 1
            else:
                videojuego.titulo = row.title
                videojuego.consola = console
                updated += 1

            publisher = _get_or_create_name(
                session, Publisher, row.publisher, publishers
            )
            developer = _get_or_create_name(
                session, Desarrollador, row.developer, developers
            )
            videojuego.publisher = publisher
            videojuego.desarrollador = developer
            videojuego.fecha_lanzamiento = row.release_date
            videojuego.ventas = row.sales
            videojuego.imagen_url = row.image_url

    return created, updated, duplicate_groups, ignored_rows


def main() -> None:
    created, updated, duplicate_groups, ignored_rows = import_games()
    print(
        f"Importación de videojuegos completada: {created} nuevos, "
        f"{updated} actualizados; {duplicate_groups} grupos duplicados "
        f"resueltos, {ignored_rows} filas ignoradas."
    )


if __name__ == "__main__":
    main()
