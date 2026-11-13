"""Fixtures compartidas: base SQLite en memoria (no toca gamestats.db)."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from data.database import get_session
from main import app
from models.base import Base
from models.consola import Consola
from models.desarrollador import Desarrollador
from models.fabricante import Fabricante
from models.generacion import Generacion
from models.publisher import Publisher
from models.videojuego import Videojuego  # noqa: F401  (registra la tabla)


@pytest.fixture()
def session_factory():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # una única conexión: la base en memoria se comparte
    )

    @event.listens_for(engine, "connect")
    def _fk(dbapi_connection, _record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    yield sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    engine.dispose()


@pytest.fixture()
def client(session_factory):
    def _get_session():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_session] = _get_session
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def datos(session_factory):
    """Datos de referencia: 2 consolas, 1 publisher y 1 desarrollador."""
    with session_factory() as s:
        fabricante = Fabricante(nombre="Nintendo")
        generacion = Generacion(numero=5)
        s.add_all([fabricante, generacion])
        s.flush()
        n64 = Consola(nombre="Nintendo 64", fabricante_id=fabricante.id, generacion_id=generacion.id)
        ps1 = Consola(nombre="PlayStation", fabricante_id=fabricante.id, generacion_id=generacion.id)
        publisher = Publisher(nombre="Nintendo")
        desarrollador = Desarrollador(nombre="Nintendo EAD")
        s.add_all([n64, ps1, publisher, desarrollador])
        s.commit()
        return {
            "n64": n64.id,
            "ps1": ps1.id,
            "publisher": publisher.id,
            "developer": desarrollador.id,
        }