from datetime import date

import pytest

from models.consola import Consola
from models.desarrollador import Desarrollador
from models.fabricante import Fabricante
from models.generacion import Generacion
from models.publisher import Publisher
from models.videojuego import Videojuego


def test_estadisticas_consolas_agrega_ventas_y_lanzamientos(client, session_factory, datos):
    with session_factory() as session:
        n64 = session.get(Consola, datos["n64"])
        playstation = session.get(Consola, datos["ps1"])
        n64.unidades_vendidas = 12.5
        n64.anio_lanzamiento = 1996
        playstation.unidades_vendidas = 102
        playstation.anio_lanzamiento = 1994
        session.commit()

    response = client.get("/api/estadisticas/consolas")

    assert response.status_code == 200
    result = response.json()
    assert result["meta"] == {
        "unit": "million_units",
        "releaseYearBasis": "console_release_year",
    }
    assert result["data"]["summary"] == {
        "consoleCount": 2,
        "manufacturerCount": 1,
        "generationCount": 1,
        "totalSales": 114.5,
    }
    assert result["data"]["salesByManufacturer"] == [
        {"name": "Nintendo", "sales": 114.5, "consoleCount": 2}
    ]
    assert result["data"]["salesByGeneration"] == [
        {"name": "Generación 5", "sales": 114.5, "consoleCount": 2}
    ]
    assert result["data"]["releasesByDecade"] == [
        {"decade": "1990s", "consoleCount": 2}
    ]
    assert result["data"]["consoles"][0]["name"] == "PlayStation"


def test_estadisticas_consolas_vacia(client):
    response = client.get("/api/estadisticas/consolas")

    assert response.status_code == 200
    assert response.json()["data"] == {
        "summary": {
            "consoleCount": 0,
            "manufacturerCount": 0,
            "generationCount": 0,
            "totalSales": 0,
        },
        "consoles": [],
        "salesByManufacturer": [],
        "salesByGeneration": [],
        "releasesByDecade": [],
    }


def poblar_juegos(session_factory, datos):
    with session_factory() as session:
        nintendo_64 = session.get(Consola, datos["n64"])
        sony = Fabricante(nombre="Sony")
        sexta_generacion = Generacion(numero=6)
        sony_publisher = Publisher(nombre="Sony")
        sony_developer = Desarrollador(nombre="Sony Studio")
        session.add_all([sony, sexta_generacion, sony_publisher, sony_developer])
        session.flush()

        ps2 = Consola(
            nombre="PlayStation 2",
            fabricante_id=sony.id,
            generacion_id=sexta_generacion.id,
        )
        session.add(ps2)
        session.flush()

        session.add_all(
            [
                Videojuego(
                    titulo="Zelda",
                    consola_id=datos["n64"],
                    publisher_id=datos["publisher"],
                    desarrollador_id=datos["developer"],
                    fecha_lanzamiento=date(1996, 6, 23),
                    ventas=12.5,
                ),
                Videojuego(
                    titulo="Final Fantasy",
                    consola_id=datos["ps1"],
                    publisher_id=sony_publisher.id,
                    desarrollador_id=sony_developer.id,
                    fecha_lanzamiento=date(1994, 12, 18),
                    ventas=102,
                ),
                Videojuego(
                    titulo="Gran Turismo",
                    consola_id=ps2.id,
                    publisher_id=sony_publisher.id,
                    desarrollador_id=sony_developer.id,
                    fecha_lanzamiento=date(2000, 3, 4),
                    ventas=50,
                ),
                Videojuego(
                    titulo="Sin ventas ni fecha",
                    consola_id=datos["n64"],
                    publisher_id=datos["publisher"],
                    ventas=None,
                ),
            ]
        )
        session.commit()
        return {
            "nintendo_manufacturer_id": nintendo_64.fabricante_id,
            "nintendo_generation_id": nintendo_64.generacion_id,
            "sony_manufacturer_id": sony.id,
            "sixth_generation_id": sexta_generacion.id,
            "sony_publisher_id": sony_publisher.id,
            "ps2_id": ps2.id,
        }


def test_estadisticas_videojuegos_agrega_y_omite_ventas_ausentes(
    client, session_factory, datos
):
    extra = poblar_juegos(session_factory, datos)

    resumen = client.get("/api/estadisticas/resumen").json()
    assert resumen == {
        "data": {
            "gameCount": 4,
            "totalSales": 164.5,
            "topConsole": {
                "id": datos["ps1"],
                "name": "PlayStation",
                "sales": 102,
            },
        },
        "meta": {"unit": "million_copies", "filters": {}},
    }

    assert client.get("/api/estadisticas/ventas-por-generacion").json()["data"] == [
        {
            "generationId": extra["nintendo_generation_id"],
            "generationNumber": 5,
            "sales": 114.5,
        },
        {
            "generationId": extra["sixth_generation_id"],
            "generationNumber": 6,
            "sales": 50,
        },
    ]
    assert client.get("/api/estadisticas/ventas-por-fabricante").json()["data"] == [
        {
            "manufacturerId": extra["nintendo_manufacturer_id"],
            "manufacturerName": "Nintendo",
            "sales": 114.5,
        },
        {
            "manufacturerId": extra["sony_manufacturer_id"],
            "manufacturerName": "Sony",
            "sales": 50,
        },
    ]
    assert client.get("/api/estadisticas/ventas-por-anio").json()["data"] == [
        {"releaseYear": 1994, "sales": 102},
        {"releaseYear": 1996, "sales": 12.5},
        {"releaseYear": 2000, "sales": 50},
    ]
    assert client.get("/api/estadisticas/ventas-por-consola").json()["data"] == [
        {"consoleId": datos["ps1"], "consoleName": "PlayStation", "sales": 102},
        {"consoleId": extra["ps2_id"], "consoleName": "PlayStation 2", "sales": 50},
        {"consoleId": datos["n64"], "consoleName": "Nintendo 64", "sales": 12.5},
    ]
    assert client.get("/api/estadisticas/juegos-mas-vendidos?limit=2").json()[
        "data"
    ] == [
        {
            "gameId": 2,
            "title": "Final Fantasy",
            "consoleName": "PlayStation",
            "releaseYear": 1994,
            "sales": 102,
        },
        {
            "gameId": 3,
            "title": "Gran Turismo",
            "consoleName": "PlayStation 2",
            "releaseYear": 2000,
            "sales": 50,
        },
    ]
    assert client.get("/api/estadisticas/dominador-por-generacion").json()["data"] == [
        {
            "generationId": extra["nintendo_generation_id"],
            "generationNumber": 5,
            "manufacturer": {
                "id": extra["nintendo_manufacturer_id"],
                "name": "Nintendo",
            },
            "sales": 114.5,
        },
        {
            "generationId": extra["sixth_generation_id"],
            "generationNumber": 6,
            "manufacturer": {"id": extra["sony_manufacturer_id"], "name": "Sony"},
            "sales": 50,
        },
    ]


def test_ranking_y_filtros_de_videojuegos(client, session_factory, datos):
    extra = poblar_juegos(session_factory, datos)

    publishers = client.get("/api/estadisticas/ranking-publishers").json()["data"]
    assert publishers[0] == {
        "publisherId": extra["sony_publisher_id"],
        "publisherName": "Sony",
        "sales": 152,
        "gameCount": 2,
    }
    assert publishers[1] == {
        "publisherId": datos["publisher"],
        "publisherName": "Nintendo",
        "sales": 12.5,
        "gameCount": 2,
    }
    developers = client.get("/api/estadisticas/ranking-desarrolladores").json()["data"]
    assert developers[0]["developerName"] == "Sony Studio"
    assert developers[0]["sales"] == 152
    assert developers[0]["gameCount"] == 2

    filtered = client.get(
        f"/api/estadisticas/resumen?yearFrom=1995&yearTo=1999&consoleId={datos['n64']}"
    ).json()
    assert filtered["data"]["gameCount"] == 1
    assert filtered["data"]["totalSales"] == 12.5
    assert filtered["meta"]["filters"] == {
        "yearFrom": 1995,
        "yearTo": 1999,
        "consoleId": datos["n64"],
    }

    combined = client.get(
        "/api/estadisticas/resumen"
        f"?generationId={extra['nintendo_generation_id']}"
        f"&manufacturerId={extra['nintendo_manufacturer_id']}"
        f"&publisherId={datos['publisher']}"
    ).json()
    assert combined["data"]["gameCount"] == 2
    assert combined["data"]["totalSales"] == 12.5

    limited = client.get("/api/estadisticas/ranking-publishers?limit=1").json()
    assert len(limited["data"]) == 1


@pytest.mark.parametrize(
    "path",
    [
        "/api/estadisticas/ventas-por-generacion",
        "/api/estadisticas/ventas-por-consola",
        "/api/estadisticas/ventas-por-fabricante",
        "/api/estadisticas/ranking-publishers",
        "/api/estadisticas/ranking-desarrolladores",
        "/api/estadisticas/ventas-por-anio",
        "/api/estadisticas/juegos-mas-vendidos",
        "/api/estadisticas/dominador-por-generacion",
    ],
)
def test_consultas_sin_juegos_devuelven_lista_vacia(client, path):
    response = client.get(path)

    assert response.status_code == 200
    assert response.json()["data"] == []


def test_resumen_sin_juegos_no_inventa_ventas(client):
    response = client.get("/api/estadisticas/resumen")

    assert response.status_code == 200
    assert response.json() == {
        "data": {"gameCount": 0, "totalSales": 0, "topConsole": None},
        "meta": {"unit": "million_copies", "filters": {}},
    }


def test_filtros_invalidos_de_estadisticas(client):
    response = client.get("/api/estadisticas/resumen?yearFrom=2010&yearTo=2000")
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_REQUEST"

    response = client.get("/api/estadisticas/juegos-mas-vendidos?limit=101")
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_REQUEST"
