def test_login_admin(client):
    response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "admin123"},
    )

    assert response.status_code == 200
    assert response.json()["user"] == {"username": "admin", "role": "admin"}
    assert response.json()["accessToken"]
    assert response.json()["expiresAt"] > 0


def test_login_usuario(client):
    response = client.post(
        "/api/auth/login",
        json={"username": "usuario", "password": "usuario123"},
    )

    assert response.status_code == 200
    assert response.json()["user"] == {"username": "usuario", "role": "user"}


def test_login_rechaza_password_incorrecta(client):
    response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "incorrecta"},
    )

    assert response.status_code == 401


def test_usuario_puede_ver_estadisticas_pero_no_el_abm(client):
    response = client.post(
        "/api/auth/login",
        json={"username": "usuario", "password": "usuario123"},
    )
    client.headers["Authorization"] = f"Bearer {response.json()['accessToken']}"

    assert client.get("/api/videojuegos").status_code == 403
    assert client.get("/api/consolas").status_code == 200
    assert client.get("/api/estadisticas/consolas").status_code == 200


def test_rutas_protegidas_rechazan_sesion_ausente(client):
    del client.headers["Authorization"]

    assert client.get("/api/estadisticas/consolas").status_code == 401
    assert client.get("/api/videojuegos").status_code == 401
