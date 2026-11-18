# Task API · Docker + GitHub Actions

[![CI/CD](https://github.com/Sastoque28-Dev/devops-task-api/actions/workflows/ci.yml/badge.svg)](https://github.com/Sastoque28-Dev/devops-task-api/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.12-blue)
![Docker](https://img.shields.io/badge/docker-compose-2496ED)
![License](https://img.shields.io/badge/license-MIT-green)

API REST de tareas (Flask + PostgreSQL) contenerizada con Docker y Docker Compose, con integración y entrega continuas mediante GitHub Actions. Proyecto de la **Actividad de aprendizaje 3**.

## Arquitectura

```
Cliente ──:8000──> [ app: Flask + Gunicorn ] ──red "backend"──> [ db: PostgreSQL 16 ]
                                                                      │
                                                                volumen "pgdata"
```

- **app**: imagen multi-stage basada en `python:3.12-slim`, usuario no root, healthcheck.
- **db**: `postgres:16-alpine`, sin puertos publicados, datos en un volumen nombrado.
- **backend**: red bridge propia; los servicios se resuelven por nombre (`db`).

## Requisitos

- Docker 24+ y Docker Compose v2
- (Opcional, para desarrollo) Python 3.12

## Instalación y uso

```bash
git clone https://github.com/Sastoque28-Dev/devops-task-api.git
cd REPO
cp .env.example .env          # edita POSTGRES_PASSWORD
docker compose up -d --build
```

Probar:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/health/db
curl http://localhost:8000/tasks
curl -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d '{"title":"Mi primera tarea"}'
curl -X PUT  http://localhost:8000/tasks/1/done
```

Comandos útiles:

```bash
docker compose ps                 # estado y salud de los servicios
docker compose logs -f app        # logs de la API
docker compose down               # detener (los datos se conservan)
docker compose down -v            # detener y BORRAR el volumen de datos
```

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/health` | Liveness (la app responde) |
| GET | `/health/db` | Readiness (conexión a PostgreSQL) |
| GET | `/tasks` | Lista las tareas |
| POST | `/tasks` | Crea una tarea (`{"title": "..."}`) |
| PUT | `/tasks/<id>/done` | Marca una tarea como completada |

## Desarrollo local y pruebas

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
```

Las pruebas usan una base de datos simulada, por lo que no necesitan Docker.

## Buenas prácticas aplicadas

- Build multi-stage y capas ordenadas para aprovechar la caché.
- Contenedor ejecutado con usuario sin privilegios.
- Secretos en `.env` (ignorado por Git); solo se versiona `.env.example`.
- Base de datos no expuesta al host; `depends_on` con `service_healthy`.
- Versiones fijadas en `requirements.txt` y en las imágenes base.
- `.dockerignore` para reducir el contexto de build.

## Flujo de trabajo (GitHub Flow)

1. Se crea un **Issue** por cada tarea.
2. Se trabaja en una rama `feature/...` o `docs/...` a partir de `main`.
3. Se abre un **Pull Request** que referencia el issue (`Closes #N`).
4. GitHub Actions ejecuta pruebas y la integración con Compose.
5. Tras el merge, `main` publica la imagen en GitHub Container Registry.
6. Las versiones se marcan con tags semánticos (`v1.0.0`).

Más detalles en la [Wiki](../../wiki): Arquitectura, Guía de Docker y CI/CD.

## Estructura

```
.
├── .github/              # workflows, plantillas de Issues y PR
├── db/init.sql           # esquema inicial de la base de datos
├── docs/                 # páginas de la Wiki e informe técnico
├── scripts/              # automatización del flujo de GitHub
├── src/                  # código de la aplicación
├── tests/                # pruebas unitarias
├── Dockerfile
├── docker-compose.yml
└── .env.example
```
