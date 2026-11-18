"""Pruebas unitarias con una base de datos simulada (no requieren Docker)."""
import pytest

from app import create_app


class FakeCursor:
    def __init__(self, rows=None, one=None, fail=False):
        self.rows, self.one, self.fail = rows or [], one, fail
        self.queries = []

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def execute(self, sql, params=None):
        if self.fail:
            raise RuntimeError("db caída")
        self.queries.append((sql, params))

    def fetchall(self):
        return self.rows

    def fetchone(self):
        return self.one


class FakeConn:
    def __init__(self, cursor):
        self._cursor = cursor

    def cursor(self):
        return self._cursor

    def commit(self):
        pass

    def rollback(self):
        pass

    def close(self):
        pass


def make_client(**cursor_kwargs):
    cursor = FakeCursor(**cursor_kwargs)
    app = create_app(lambda: FakeConn(cursor))
    return app.test_client(), cursor


def test_health_no_toca_la_base_de_datos():
    client, cursor = make_client(fail=True)
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json() == {"status": "ok"}
    assert cursor.queries == []


def test_health_db_ok():
    client, _ = make_client()
    assert client.get("/health/db").status_code == 200


def test_health_db_caida_devuelve_503():
    client, _ = make_client(fail=True)
    assert client.get("/health/db").status_code == 503


def test_listar_tareas():
    client, _ = make_client(rows=[(1, "Estudiar Docker", False)])
    res = client.get("/tasks")
    assert res.get_json() == [{"id": 1, "title": "Estudiar Docker", "done": False}]


def test_crear_tarea():
    client, cursor = make_client(one=(7, "Hacer informe", False))
    res = client.post("/tasks", json={"title": "  Hacer informe "})
    assert res.status_code == 201
    assert res.get_json()["id"] == 7
    assert cursor.queries[0][1] == ("Hacer informe",)


@pytest.mark.parametrize("payload", [{}, {"title": ""}, {"title": "   "}])
def test_crear_tarea_sin_titulo(payload):
    client, _ = make_client()
    assert client.post("/tasks", json=payload).status_code == 400


def test_completar_tarea():
    client, _ = make_client(one=(1, "x", True))
    assert client.put("/tasks/1/done").get_json()["done"] is True


def test_completar_tarea_inexistente():
    client, _ = make_client(one=None)
    assert client.put("/tasks/99/done").status_code == 404
