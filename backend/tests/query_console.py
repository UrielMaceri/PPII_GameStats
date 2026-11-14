from __future__ import annotations

import sys

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from data.database import DATABASE_PATH, SessionLocal
from models import Consola, Videojuego


def _show(value: object | None) -> str:
    return "No disponible" if value is None else str(value)


def print_console_details(session: Session, console_id: int) -> bool:
    statement = (
        select(Consola)
        .where(Consola.id == console_id)
        .options(
            joinedload(Consola.fabricante),
            joinedload(Consola.generacion),
            selectinload(Consola.videojuegos)
            .joinedload(Videojuego.publisher),
            selectinload(Consola.videojuegos)
            .joinedload(Videojuego.desarrollador),
        )
    )
    console = session.scalar(statement)
    if console is None:
        return False

    generation = console.generacion
    generation_years = (
        f"{_show(generation.anio_inicio)} - {_show(generation.anio_fin)}"
    )
    production_status = (
        "Sí"
        if console.sigue_en_produccion is True
        else "No"
        if console.sigue_en_produccion is False
        else "Desconocido"
    )

    print(f"\nConsola #{console.id}: {console.nombre}")
    print(f"  Tipo: {_show(console.tipo)}")
    print(f"  Fabricante #{console.fabricante.id}: {console.fabricante.nombre}")
    print(f"    País: {_show(console.fabricante.pais)}")
    print(
        f"  Generación #{generation.id}: "
        f"{_show(generation.etiqueta)} (número {generation.numero})"
    )
    print(f"    Años de la generación: {generation_years}")
    print(f"  Año de lanzamiento: {_show(console.anio_lanzamiento)}")
    print(f"  Año de discontinuación: {_show(console.anio_descontinuacion)}")
    print(f"  Sigue en producción: {production_status}")
    print(
        "  Unidades vendidas (millones): "
        f"{_show(console.unidades_vendidas)}"
    )
    print(f"  Descripción: {_show(console.descripcion)}")
    print(f"  GIF: {_show(console.gif_url)}")

    print(f"\n  Videojuegos asociados ({len(console.videojuegos)}):")
    if not console.videojuegos:
        print("    No hay videojuegos asociados a esta consola.")
    else:
        for game in sorted(console.videojuegos, key=lambda item: item.id):
            release_date = (
                game.fecha_lanzamiento.isoformat()
                if game.fecha_lanzamiento is not None
                else None
            )
            publisher = (
                f"#{game.publisher.id}: {game.publisher.nombre}"
                if game.publisher is not None
                else "No disponible"
            )
            developer = (
                f"#{game.desarrollador.id}: {game.desarrollador.nombre}"
                if game.desarrollador is not None
                else "No disponible"
            )
            print(f"    Videojuego #{game.id}: {game.titulo}")
            print(f"      Fecha de lanzamiento: {_show(release_date)}")
            print(f"      Ventas: {_show(game.ventas)}")
            print(f"      Imagen: {_show(game.imagen_url)}")
            print(f"      Publisher: {publisher}")
            print(f"      Desarrollador: {developer}")

    return True


def main() -> None:
    sys.stdout.reconfigure(errors="backslashreplace")

    if not DATABASE_PATH.is_file():
        print("No se encontró la base de datos.")
        print("Ejecuta BUILD.bat para crearla y cargar las consolas primero.")
        return

    raw_console_id = input("Ingrese el ID de la consola (o 'q' para salir): ").strip()
    if raw_console_id.casefold() == "q":
        return

    try:
        console_id = int(raw_console_id)
    except ValueError:
        print("El ID debe ser un número entero.")
        return

    if console_id <= 0:
        print("El ID debe ser un entero positivo.")
        return

    with SessionLocal() as session:
        found = print_console_details(session, console_id)

    if not found:
        print(f"No existe una consola con ID {console_id}.")


if __name__ == "__main__":
    main()
