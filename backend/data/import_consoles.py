from __future__ import annotations

import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from data.database import SessionLocal, engine
from models import Base, Consola, Fabricante, Generacion

CSV_PATH = Path(__file__).resolve().parent / "docs" / "Console_Data.csv"

MANUFACTURER_COUNTRIES = {
    "Magnavox": "Estados Unidos",
    "Atari": "Estados Unidos",
    "Mattel": "Estados Unidos",
    "Nintendo": "Japón",
    "Sega": "Japón",
    "Sony": "Japón",
    "Microsoft": "Estados Unidos",
}

REQUIRED_COLUMNS = {
    "Console Name",
    "Type",
    "Company",
    "Gen",
    "Gen Years",
    "Released Year",
    "Generation",
    "Discontinuation Year",
    "Units sold (million)",
    "Remarks",
    "Link to gif",
}


def _required_text(row: dict[str, str | None], column: str, line: int) -> str:
    value = row.get(column)
    if value is None or not value.strip():
        raise ValueError(f"Fila {line}: falta el valor obligatorio '{column}'.")
    return value.strip()


def _optional_text(row: dict[str, str | None], column: str) -> str | None:
    value = row.get(column)
    if value is None or not value.strip():
        return None
    return value.strip()


def _parse_year(value: str, column: str, line: int) -> int:
    try:
        year = int(value)
    except ValueError as error:
        raise ValueError(
            f"Fila {line}: '{column}' debe ser un año entero, se recibió {value!r}."
        ) from error
    if not 1 <= year <= 9999:
        raise ValueError(f"Fila {line}: el año de '{column}' está fuera de rango.")
    return year


def _parse_generation_years(
    row: dict[str, str | None], line: int
) -> tuple[int, int | None]:
    value = _required_text(row, "Gen Years", line)
    parts = value.split("-", maxsplit=1)
    if len(parts) != 2:
        raise ValueError(
            f"Fila {line}: 'Gen Years' debe tener el formato 'año-año', "
            f"se recibió {value!r}."
        )
    start = _parse_year(parts[0].strip(), "Gen Years", line)
    end_text = parts[1].strip()
    if end_text.casefold() == "ongoing":
        end = None
    else:
        end = _parse_year(end_text, "Gen Years", line)
    if end is not None and start > end:
        raise ValueError(f"Fila {line}: 'Gen Years' comienza después de terminar.")
    return start, end


def _parse_sales(row: dict[str, str | None], line: int) -> Decimal | None:
    value = _optional_text(row, "Units sold (million)")
    if value is None:
        return None
    try:
        sales = Decimal(value)
    except InvalidOperation as error:
        raise ValueError(
            f"Fila {line}: ventas inválidas en 'Units sold (million)': {value!r}."
        ) from error
    if not sales.is_finite() or sales < 0:
        raise ValueError(
            f"Fila {line}: las ventas deben ser un número finito no negativo."
        )
    return sales


def _parse_discontinuation(
    row: dict[str, str | None], line: int
) -> tuple[int | None, bool | None]:
    value = _optional_text(row, "Discontinuation Year")
    if value is None:
        return None, None
    if value.casefold() == "ongoing":
        return None, True
    return _parse_year(value, "Discontinuation Year", line), False


def _get_or_create_manufacturer(
    session: Session,
    name: str,
    country: str,
    cache: dict[str, Fabricante],
) -> Fabricante:
    manufacturer = cache.get(name)
    if manufacturer is None:
        manufacturer = session.scalar(
            select(Fabricante).where(Fabricante.nombre == name)
        )
        if manufacturer is None:
            manufacturer = Fabricante(nombre=name, pais=country)
            session.add(manufacturer)
        cache[name] = manufacturer
    manufacturer.pais = country
    return manufacturer


def _get_or_create_generation(
    session: Session,
    number: int,
    label: str | None,
    year_range: tuple[int, int | None],
    cache: dict[int, Generacion],
) -> Generacion:
    generation = cache.get(number)
    if generation is None:
        generation = session.scalar(
            select(Generacion).where(Generacion.numero == number)
        )
        if generation is None:
            generation = Generacion(numero=number)
            session.add(generation)
        cache[number] = generation

    generation.etiqueta = label
    generation.anio_inicio, generation.anio_fin = year_range
    return generation


def import_consoles(csv_path: Path = CSV_PATH) -> tuple[int, int]:
    Base.metadata.create_all(engine)

    created = 0
    updated = 0
    manufacturers: dict[str, Fabricante] = {}
    generations: dict[int, Generacion] = {}
    seen_names: set[str] = set()

    with csv_path.open(encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        columns = set(reader.fieldnames or [])
        missing_columns = REQUIRED_COLUMNS - columns
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(f"Faltan columnas requeridas en el CSV: {missing}.")

        with SessionLocal.begin() as session:
            for line, row in enumerate(reader, start=2):
                name = _required_text(row, "Console Name", line)
                if name in seen_names:
                    raise ValueError(
                        f"Fila {line}: el CSV repite el nombre de consola {name!r}."
                    )
                seen_names.add(name)

                manufacturer_name = _required_text(row, "Company", line)
                manufacturer_country = MANUFACTURER_COUNTRIES.get(manufacturer_name)
                if manufacturer_country is None:
                    raise ValueError(
                        f"Fila {line}: no hay un país definido para el fabricante "
                        f"{manufacturer_name!r}."
                    )
                generation_number = _parse_year(
                    _required_text(row, "Generation", line), "Generation", line
                )
                if not 1 <= generation_number <= 9:
                    raise ValueError(
                        f"Fila {line}: 'Generation' debe estar entre 1 y 9."
                    )
                generation = _get_or_create_generation(
                    session,
                    generation_number,
                    _optional_text(row, "Gen"),
                    _parse_generation_years(row, line),
                    generations,
                )
                manufacturer = _get_or_create_manufacturer(
                    session,
                    manufacturer_name,
                    manufacturer_country,
                    manufacturers,
                )

                console = session.scalar(
                    select(Consola).where(Consola.nombre == name)
                )
                if console is None:
                    console = Consola(nombre=name)
                    session.add(console)
                    created += 1
                else:
                    updated += 1

                console.tipo = _optional_text(row, "Type")
                console.fabricante = manufacturer
                console.generacion = generation
                released_year = _optional_text(row, "Released Year")
                discontinued_year, still_in_production = _parse_discontinuation(
                    row, line
                )
                console.anio_lanzamiento = (
                    _parse_year(released_year, "Released Year", line)
                    if released_year is not None
                    else None
                )
                console.anio_descontinuacion = discontinued_year
                console.sigue_en_produccion = still_in_production
                console.unidades_vendidas = _parse_sales(row, line)
                console.descripcion = _optional_text(row, "Remarks")
                console.gif_url = _optional_text(row, "Link to gif")

            if not seen_names:
                raise ValueError("El CSV no contiene filas para importar.")

    return created, updated


def main() -> None:
    created, updated = import_consoles()
    print(
        f"Importación completada: {created} consolas nuevas, "
        f"{updated} actualizadas. Base: {engine.url.database}"
    )


if __name__ == "__main__":
    main()
