import pytest

URL = "/api/videojuegos"


# ---------- ayudas ----------
def cuerpo(datos, **cambios):
    base = {
        "title": "Super Mario 64",
        "consoleId": datos["n64"],
        "publisherId": None,
        "developerId": None,
        "releaseYear": 1996,
        "sales": 11.91,
    }
    base.update(cambios)
    return base


def crear(client, datos, **cambios):
    r = client.post(URL, json=cuerpo(datos, **cambios))
    assert r.status_code == 201, r.text
    return r.json()["data"]


def campos_con_error(respuesta):
    return {d["field"] for d in respuesta.json()["error"]["details"]}


def titulos(respuesta):
    return [v["title"] for v in respuesta.json()["data"]]


def poblar(client, datos):
    """5 juegos para probar listado, paginación y filtros."""
    crear(client, datos, title="Super Mario 64", publisherId=datos["publisher"])
    crear(client, datos, title="Mario Kart 64", publisherId=datos["publisher"])
    crear(client, datos, title="Crash Bandicoot", consoleId=datos["ps1"])
    crear(client, datos, title="Zelda OoT", publisherId=datos["publisher"], releaseYear=1998)
    crear(client, datos, title="Sin Año", consoleId=datos["ps1"], releaseYear=None)


# ---------- alta ----------
def test_crear_valido(client, datos):
    r = client.post(URL, json=cuerpo(datos))
    assert r.status_code == 201
    v = r.json()["data"]
    assert set(v) == {"id", "title", "console", "publisher", "developer", "releaseYear", "sales"}
    assert v["id"] > 0
    assert v["title"] == "Super Mario 64"
    assert v["console"] == {"id": datos["n64"], "name": "Nintendo 64"}
    assert v["publisher"] is None
    assert v["developer"] is None
    assert v["releaseYear"] == 1996
    assert v["sales"] == 11.91


def test_crear_con_publisher_y_developer(client, datos):
    v = crear(client, datos, publisherId=datos["publisher"], developerId=datos["developer"])
    assert v["publisher"] == {"id": datos["publisher"], "name": "Nintendo"}
    assert v["developer"] == {"id": datos["developer"], "name": "Nintendo EAD"}


def test_crear_solo_campos_obligatorios(client, datos):
    r = client.post(URL, json={"title": "Solo lo básico", "consoleId": datos["n64"]})
    assert r.status_code == 201
    v = r.json()["data"]
    assert v["publisher"] is None
    assert v["developer"] is None
    assert v["releaseYear"] is None
    assert v["sales"] is None


def test_crear_limpia_espacios_del_titulo(client, datos):
    v = crear(client, datos, title="  Super   Mario  64 ")
    assert v["title"] == "Super Mario 64"


@pytest.mark.parametrize(
    "cambios, campo",
    [
        ({"title": ""}, "title"),
        ({"title": "   "}, "title"),
        ({"title": "x" * 256}, "title"),
        ({"consoleId": 0}, "consoleId"),
        ({"sales": -5}, "sales"),
        ({"sales": "abc"}, "sales"),
        ({"releaseYear": 99}, "releaseYear"),
        ({"releaseYear": 1996.5}, "releaseYear"),
        ({"publisherId": 0}, "publisherId"),
    ],
)
def test_crear_campos_invalidos(client, datos, cambios, campo):
    r = client.post(URL, json=cuerpo(datos, **cambios))
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "VALIDATION_ERROR"
    assert campo in campos_con_error(r)


def test_crear_sin_campos_obligatorios(client):
    r = client.post(URL, json={})
    assert r.status_code == 422
    assert campos_con_error(r) == {"title", "consoleId"}


def test_crear_con_json_invalido(client):
    r = client.post(URL, content="{no es json", headers={"Content-Type": "application/json"})
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "VALIDATION_ERROR"


def test_crear_con_relaciones_inexistentes(client, datos):
    r = client.post(URL, json=cuerpo(datos, consoleId=999, publisherId=999, developerId=999))
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "VALIDATION_ERROR"
    assert campos_con_error(r) == {"consoleId", "publisherId", "developerId"}


def test_crear_duplicado_en_la_misma_consola(client, datos):
    crear(client, datos)
    r = client.post(URL, json=cuerpo(datos))
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "DUPLICATE_RESOURCE"
    assert "title" in campos_con_error(r)


def test_duplicado_ignora_mayusculas(client, datos):
    crear(client, datos)
    r = client.post(URL, json=cuerpo(datos, title="SUPER MARIO 64"))
    assert r.status_code == 409


def test_mismo_titulo_en_otra_consola_es_valido(client, datos):
    crear(client, datos)
    crear(client, datos, consoleId=datos["ps1"])


# ---------- detalle ----------
def test_obtener_existente(client, datos):
    v = crear(client, datos)
    r = client.get(f"{URL}/{v['id']}")
    assert r.status_code == 200
    assert r.json() == {"data": v}


def test_obtener_inexistente(client):
    r = client.get(f"{URL}/999")
    assert r.status_code == 404
    error = r.json()["error"]
    assert error["code"] == "NOT_FOUND"
    assert error["details"] == []


def test_obtener_con_id_no_numerico(client):
    r = client.get(f"{URL}/abc")
    assert r.status_code == 400
    assert r.json()["error"]["code"] == "INVALID_REQUEST"


# ---------- edición ----------
def test_actualizar_valido(client, datos):
    v = crear(client, datos)
    r = client.put(
        f"{URL}/{v['id']}", json=cuerpo(datos, sales=12.5, publisherId=datos["publisher"])
    )
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["id"] == v["id"]
    assert data["sales"] == 12.5
    assert data["publisher"]["name"] == "Nintendo"
    assert client.get(f"{URL}/{v['id']}").json()["data"]["sales"] == 12.5


def test_actualizar_permite_dejar_campos_vacios(client, datos):
    v = crear(client, datos, publisherId=datos["publisher"])
    r = client.put(f"{URL}/{v['id']}", json=cuerpo(datos, publisherId=None, sales=None))
    assert r.status_code == 200
    assert r.json()["data"]["publisher"] is None
    assert r.json()["data"]["sales"] is None


def test_actualizar_inexistente(client, datos):
    r = client.put(f"{URL}/999", json=cuerpo(datos))
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "NOT_FOUND"


def test_actualizar_exige_el_objeto_completo(client, datos):
    v = crear(client, datos)
    r = client.put(f"{URL}/{v['id']}", json={"title": "Nuevo", "consoleId": datos["n64"]})
    assert r.status_code == 422
    assert {"publisherId", "developerId", "releaseYear", "sales"} <= campos_con_error(r)


def test_actualizar_a_un_titulo_duplicado(client, datos):
    crear(client, datos, title="Super Mario 64")
    otro = crear(client, datos, title="Mario Kart 64")
    r = client.put(f"{URL}/{otro['id']}", json=cuerpo(datos, title="Super Mario 64"))
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "DUPLICATE_RESOURCE"


def test_actualizar_con_relaciones_inexistentes(client, datos):
    v = crear(client, datos)
    r = client.put(f"{URL}/{v['id']}", json=cuerpo(datos, consoleId=999, developerId=999))
    assert r.status_code == 422
    assert campos_con_error(r) == {"consoleId", "developerId"}


# ---------- baja ----------
def test_eliminar(client, datos):
    v = crear(client, datos)
    r = client.delete(f"{URL}/{v['id']}")
    assert r.status_code == 204
    assert r.content == b""
    assert client.get(f"{URL}/{v['id']}").status_code == 404
    assert client.delete(f"{URL}/{v['id']}").status_code == 404


# ---------- listado ----------
def test_listado_vacio_no_es_error(client):
    r = client.get(URL)
    assert r.status_code == 200
    assert r.json() == {
        "data": [],
        "pagination": {"page": 1, "pageSize": 20, "totalItems": 0, "totalPages": 0},
    }


def test_listado_ordenado_por_titulo(client, datos):
    poblar(client, datos)
    r = client.get(URL)
    assert titulos(r) == [
        "Crash Bandicoot",
        "Mario Kart 64",
        "Sin Año",
        "Super Mario 64",
        "Zelda OoT",
    ]
    assert r.json()["pagination"] == {
        "page": 1,
        "pageSize": 20,
        "totalItems": 5,
        "totalPages": 1,
    }


def test_paginacion(client, datos):
    poblar(client, datos)
    p1 = client.get(URL, params={"pageSize": 2, "page": 1})
    p2 = client.get(URL, params={"pageSize": 2, "page": 2})
    p3 = client.get(URL, params={"pageSize": 2, "page": 3})
    p4 = client.get(URL, params={"pageSize": 2, "page": 4})
    assert titulos(p1) == ["Crash Bandicoot", "Mario Kart 64"]
    assert titulos(p2) == ["Sin Año", "Super Mario 64"]
    assert titulos(p3) == ["Zelda OoT"]
    assert p1.json()["pagination"] == {"page": 1, "pageSize": 2, "totalItems": 5, "totalPages": 3}
    assert p4.status_code == 200 and titulos(p4) == []  # página fuera de rango: vacía, no error
    assert p4.json()["pagination"]["totalItems"] == 5


def test_busqueda_por_titulo(client, datos):
    poblar(client, datos)
    assert titulos(client.get(URL, params={"search": "mario"})) == ["Mario Kart 64", "Super Mario 64"]
    assert titulos(client.get(URL, params={"search": "MARIO"})) == ["Mario Kart 64", "Super Mario 64"]


def test_busqueda_trata_el_porcentaje_como_texto(client, datos):
    poblar(client, datos)
    r = client.get(URL, params={"search": "%"})
    assert r.status_code == 200
    assert titulos(r) == []


def test_filtro_por_consola(client, datos):
    poblar(client, datos)
    r = client.get(URL, params={"consoleId": datos["ps1"]})
    assert titulos(r) == ["Crash Bandicoot", "Sin Año"]


def test_filtro_por_publisher(client, datos):
    poblar(client, datos)
    r = client.get(URL, params={"publisherId": datos["publisher"]})
    assert titulos(r) == ["Mario Kart 64", "Super Mario 64", "Zelda OoT"]


def test_filtro_por_anios_es_inclusivo(client, datos):
    poblar(client, datos)
    exacto = client.get(URL, params={"yearFrom": 1996, "yearTo": 1996})
    desde = client.get(URL, params={"yearFrom": 1997})
    hasta = client.get(URL, params={"yearTo": 1996})
    assert titulos(exacto) == ["Crash Bandicoot", "Mario Kart 64", "Super Mario 64"]
    assert titulos(desde) == ["Zelda OoT"]  # "Sin Año" no tiene año: queda afuera
    assert titulos(hasta) == ["Crash Bandicoot", "Mario Kart 64", "Super Mario 64"]


def test_filtros_combinados(client, datos):
    poblar(client, datos)
    r = client.get(
        URL,
        params={
            "search": "mario",
            "consoleId": datos["n64"],
            "publisherId": datos["publisher"],
            "yearFrom": 1996,
            "yearTo": 1996,
        },
    )
    assert titulos(r) == ["Mario Kart 64", "Super Mario 64"]
    assert r.json()["pagination"]["totalItems"] == 2


def test_filtros_sin_resultados_devuelven_lista_vacia(client, datos):
    poblar(client, datos)
    r = client.get(URL, params={"search": "mario", "consoleId": datos["ps1"]})
    assert r.status_code == 200
    assert r.json()["data"] == []
    assert r.json()["pagination"]["totalItems"] == 0


@pytest.mark.parametrize(
    "params",
    [
        {"page": 0},
        {"page": "abc"},
        {"pageSize": 0},
        {"pageSize": 101},
        {"yearFrom": 999},
        {"consoleId": 0},
        {"yearFrom": 2000, "yearTo": 1990},
    ],
)
def test_listado_con_parametros_invalidos(client, params):
    r = client.get(URL, params=params)
    assert r.status_code == 400
    assert r.json()["error"]["code"] == "INVALID_REQUEST"