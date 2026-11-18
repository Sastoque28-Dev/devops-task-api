"""API REST de tareas (Flask + PostgreSQL).

La aplicación es deliberadamente pequeña: el objetivo del proyecto es la
infraestructura (Docker, Compose, CI/CD), no la lógica de negocio.
"""
import os
from contextlib import contextmanager

import psycopg2
from flask import Flask, jsonify, request


def get_conn():
    """Crea una conexión a PostgreSQL leyendo la configuración del entorno."""
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB", "tasks"),
        user=os.getenv("POSTGRES_USER", "app"),
        password=os.environ["POSTGRES_PASSWORD"],
        connect_timeout=3,
    )


@contextmanager
def db_cursor(conn_factory):
    """Entrega un cursor y garantiza commit/rollback y cierre de la conexión."""
    conn = conn_factory()
    try:
        with conn.cursor() as cur:
            yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def row_to_dict(row):
    return {"id": row[0], "title": row[1], "done": row[2]}


def create_app(conn_factory=get_conn):
    app = Flask(__name__)

    @app.get("/health")
    def health():
        """Liveness: la app responde (no toca la base de datos)."""
        return jsonify(status="ok")

    @app.get("/health/db")
    def health_db():
        """Readiness: la app puede hablar con la base de datos."""
        try:
            with db_cursor(conn_factory) as cur:
                cur.execute("SELECT 1")
            return jsonify(status="ok", database="up")
        except Exception:
            return jsonify(status="error", database="down"), 503

    @app.get("/tasks")
    def list_tasks():
        with db_cursor(conn_factory) as cur:
            cur.execute("SELECT id, title, done FROM tasks ORDER BY id")
            rows = cur.fetchall()
        return jsonify([row_to_dict(r) for r in rows])

    @app.post("/tasks")
    def create_task():
        data = request.get_json(silent=True) or {}
        title = str(data.get("title", "")).strip()
        if not title:
            return jsonify(error="El campo 'title' es obligatorio"), 400
        with db_cursor(conn_factory) as cur:
            cur.execute(
                "INSERT INTO tasks (title) VALUES (%s) RETURNING id, title, done",
                (title,),
            )
            row = cur.fetchone()
        return jsonify(row_to_dict(row)), 201

    @app.put("/tasks/<int:task_id>/done")
    def complete_task(task_id):
        with db_cursor(conn_factory) as cur:
            cur.execute(
                "UPDATE tasks SET done = TRUE WHERE id = %s RETURNING id, title, done",
                (task_id,),
            )
            row = cur.fetchone()
        if row is None:
            return jsonify(error="Tarea no encontrada"), 404
        return jsonify(row_to_dict(row))

    return app


app = create_app()
