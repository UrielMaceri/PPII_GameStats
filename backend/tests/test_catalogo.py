import pytest


def test_consolas_ordenadas_por_nombre(client, datos):
    r = client.get("/api/consolas")
    assert r.status_code == 200
    assert r.json() == {
        "data": [
            {"id": datos["n64"], "name": "Nintendo 64"},
            {"id": datos["ps1"], "name": "PlayStation"},
        ]
    }  # sin "pagination": los selectores no son paginados


def test_publishers(client, datos):
    r = client.get("/api/publishers")
    assert r.status_code == 200
    assert r.json() == {"data": [{"id": datos["publisher"], "name": "Nintendo"}]}


def test_desarrolladores(client, datos):
    r = client.get("/api/desarrolladores")
    assert r.status_code == 200
    assert r.json() == {"data": [{"id": datos["developer"], "name": "Nintendo EAD"}]}


@pytest.mark.parametrize("ruta", ["/api/consolas", "/api/publishers", "/api/desarrolladores"])
def test_selectores_vacios_no_son_error(client, ruta):
    r = client.get(ruta)
    assert r.status_code == 200
    assert r.json() == {"data": []}