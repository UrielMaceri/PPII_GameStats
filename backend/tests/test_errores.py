def test_ruta_inexistente_usa_formato_del_contrato(client):
    r = client.get("/api/loquesea")
    assert r.status_code == 404
    error = r.json()["error"]
    assert set(error) == {"code", "message", "details"}
    assert error["code"] == "NOT_FOUND"
    assert error["details"] == []


def test_metodo_no_permitido(client):
    r = client.delete("/api/consolas")
    assert r.status_code == 405
    assert r.json()["error"]["code"] == "INVALID_REQUEST"