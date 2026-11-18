# Arquitectura

## Componentes

| Servicio | Imagen | Rol | Puerto publicado |
|----------|--------|-----|------------------|
| `app` | construida desde el `Dockerfile` | API REST (Flask + Gunicorn) | 8000 |
| `db` | `postgres:16-alpine` | Base de datos relacional | ninguno |

## Diagrama

```
Host ──:8000──> app ──(red backend)──> db ──> volumen pgdata
```

## Red

Compose crea la red `backend` (bridge). Dentro de ella cada servicio es accesible por su nombre mediante el DNS interno de Docker: la app se conecta a `db:5432`. Como `db` no publica puertos, solo la app puede llegar a ella.

## Volúmenes

- `pgdata`: volumen nombrado con los datos de PostgreSQL. Persiste entre reinicios y `docker compose down`; se elimina solo con `down -v`.
- `./db/init.sql`: montado en modo solo lectura en `/docker-entrypoint-initdb.d/`; crea la tabla `tasks` la primera vez.

## Orden de arranque

`app` declara `depends_on: db: condition: service_healthy`. El healthcheck de `db` usa `pg_isready`, así que la API nunca arranca antes de que PostgreSQL acepte conexiones.

## Portabilidad y consistencia

La misma imagen corre idéntica en el portátil del desarrollador, en el runner de GitHub Actions y en un servidor, porque todas las dependencias y versiones viajan dentro del contenedor.
