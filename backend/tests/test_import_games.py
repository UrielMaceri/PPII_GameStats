import csv
from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker

from data import import_games
from models import (
    Base,
    Consola,
    Desarrollador,
    Fabricante,
    Generacion,
    Publisher,
    Videojuego,
)


FIELDNAMES = [
    "Game Name",
    "System Full",
    "Units(m)",
    "Publisher",
    "Developer",
    "Image_URL",
    "Release Date",
]


@pytest.fixture()
def isolated_database(monkeypatch):
    test_engine = create_engine("sqlite://")
    Base.metadata.create_all(test_engine)
    test_sessions = sessionmaker(
        bind=test_engine, autoflush=False, expire_on_commit=False
    )
    with test_sessions.begin() as session:
        manufacturer = Fabricante(nombre="Atari")
        generation = Generacion(numero=2)
        session.add_all([manufacturer, generation])
        session.flush()
        session.add_all(
            [
                Consola(
                    nombre="Atari 2600",
                    fabricante=manufacturer,
                    generacion=generation,
                ),
                Consola(
                    nombre="Nintendo 64",
                    fabricante=manufacturer,
                    generacion=generation,
                ),
            ]
        )

    monkeypatch.setattr(import_games, "engine", test_engine)
    monkeypatch.setattr(import_games, "SessionLocal", test_sessions)
    yield test_sessions
    test_engine.dispose()


def _write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def test_import_games_resolves_duplicates_and_is_repeatable(
    isolated_database, tmp_path
):
    csv_path = tmp_path / "games.csv"
    _write_csv(
        csv_path,
        [
            {
                "Game Name": "Chrono Quest",
                "System Full": "Nintendo 64",
                "Units(m)": "1.0",
                "Publisher": "Unknown",
                "Developer": "Studio",
                "Image_URL": "",
                "Release Date": "02/01/1995",
            },
            {
                "Game Name": "Chrono Quest",
                "System Full": "Nintendo 64",
                "Units(m)": "99.0",
                "Publisher": "Later Publisher",
                "Developer": "Studio",
                "Image_URL": "https://example.test/later.jpg",
                "Release Date": "03/01/1995",
            },
            {
                "Game Name": "Same Day",
                "System Full": "Nintendo 64",
                "Units(m)": "1.0",
                "Publisher": "Unknown",
                "Developer": "Studio",
                "Image_URL": "",
                "Release Date": "04/01/1995",
            },
            {
                "Game Name": "Same Day",
                "System Full": "Nintendo 64",
                "Units(m)": "2.0",
                "Publisher": "Preferred Publisher",
                "Developer": "Studio",
                "Image_URL": "https://example.test/preferred.jpg",
                "Release Date": "04/01/1995",
            },
            {
                "Game Name": "Cross Console",
                "System Full": "Nintendo 64",
                "Units(m)": "3.0",
                "Publisher": "N/A",
                "Developer": "N/A",
                "Image_URL": "",
                "Release Date": "",
            },
            {
                "Game Name": "Cross Console",
                "System Full": "Atari 2600",
                "Units(m)": "4.0",
                "Publisher": "Atari",
                "Developer": "Activision",
                "Image_URL": "https://example.test/cross-console.jpg",
                "Release Date": "05/01/1995",
            },
            {
                "Game Name": "Unreported Sales",
                "System Full": "Nintendo 64",
                "Units(m)": "0.0",
                "Publisher": "Unknown",
                "Developer": "N/A",
                "Image_URL": "",
                "Release Date": "",
            },
        ],
    )

    result = import_games.import_games(csv_path)
    assert result == (5, 0, 2, 2)

    with isolated_database() as session:
        games = session.scalars(select(Videojuego).order_by(Videojuego.titulo)).all()
        assert len(games) == 5
        earliest = next(game for game in games if game.titulo == "Chrono Quest")
        assert earliest.fecha_lanzamiento == date(1995, 1, 2)
        assert earliest.ventas == Decimal("1.0000")
        assert earliest.publisher is None

        same_day = next(game for game in games if game.titulo == "Same Day")
        assert same_day.publisher.nombre == "Preferred Publisher"
        assert same_day.ventas == Decimal("2.0000")
        assert same_day.imagen_url == "https://example.test/preferred.jpg"

        cross_console = [game for game in games if game.titulo == "Cross Console"]
        assert len({game.consola.nombre for game in cross_console}) == 2
        assert sum(game.desarrollador is None for game in cross_console) == 1

        unreported = next(
            game for game in games if game.titulo == "Unreported Sales"
        )
        assert unreported.ventas is None

    assert import_games.import_games(csv_path) == (0, 5, 2, 2)

    with isolated_database() as session:
        assert session.scalar(select(func.count()).select_from(Videojuego)) == 5
        assert session.scalar(select(func.count()).select_from(Publisher)) == 2
        assert session.scalar(select(func.count()).select_from(Desarrollador)) == 2


def test_import_games_aborts_if_console_is_missing(isolated_database, tmp_path):
    csv_path = tmp_path / "games.csv"
    _write_csv(
        csv_path,
        [
            {
                "Game Name": "Unknown Console Game",
                "System Full": "Missing Console",
                "Units(m)": "1.0",
                "Publisher": "Publisher",
                "Developer": "Developer",
                "Image_URL": "",
                "Release Date": "",
            }
        ],
    )

    with pytest.raises(ValueError, match="no existe la consola"):
        import_games.import_games(csv_path)

    with isolated_database() as session:
        assert session.scalar(select(func.count()).select_from(Videojuego)) == 0
        assert session.scalar(select(func.count()).select_from(Publisher)) == 0
        assert session.scalar(select(func.count()).select_from(Desarrollador)) == 0
